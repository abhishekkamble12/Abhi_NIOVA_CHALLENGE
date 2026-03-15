"""
Lambda Handler: Video Uploaded → Detect Scenes → Generate Captions → Store Embeddings
=======================================================================================
Uses Amazon Nova models:
  Embeddings → Nova Multimodal Embeddings (invoke_model)
"""
import json
import os
import boto3
from services.aurora_service import get_db_session
from services.s3_service import get_s3_service
from services.event_service import get_event_service

rekognition = boto3.client('rekognition', region_name=os.getenv('AWS_REGION', 'us-east-1'))
transcribe = boto3.client('transcribe', region_name=os.getenv('AWS_REGION', 'us-east-1'))
bedrock = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION', 'us-east-1'))

NOVA_EMBEDDING_MODEL = os.getenv('NOVA_EMBEDDING_MODEL', 'amazon.nova-2-multimodal-embeddings-v1:0')


async def detect_scenes(s3_key: str) -> list:
    """Detect scenes using Rekognition."""
    response = rekognition.start_segment_detection(
        Video={'S3Object': {'Bucket': 'hivemind-media', 'Name': s3_key}},
        SegmentTypes=['SHOT'],
    )
    job_id = response['JobId']

    result = rekognition.get_segment_detection(JobId=job_id)
    return [
        {
            'start_time': seg['StartTimestampMillis'] / 1000,
            'end_time': seg['EndTimestampMillis'] / 1000,
            'confidence': seg['ShotSegment']['Confidence'],
        }
        for seg in result['Segments']
    ]


async def generate_captions(s3_key: str) -> str:
    """Generate captions using Transcribe."""
    job_name = f"transcribe-{s3_key.replace('/', '-')}"
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': f"s3://hivemind-media/{s3_key}"},
        MediaFormat='mp4',
        LanguageCode='en-US',
    )

    result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    transcript_uri = result['TranscriptionJob']['Transcript']['TranscriptFileUri']

    import urllib.request
    with urllib.request.urlopen(transcript_uri) as response:
        transcript = json.loads(response.read())

    return transcript['results']['transcripts'][0]['transcript']


async def generate_scene_embeddings(scenes: list, captions: str) -> list:
    """Generate embeddings for each scene using Amazon Nova Multimodal Embeddings."""
    embeddings = []
    for scene in scenes:
        text = f"Scene {scene['start_time']}-{scene['end_time']}: {captions}"
        response = bedrock.invoke_model(
            modelId=NOVA_EMBEDDING_MODEL,
            body=json.dumps({
                'input': text,
                'inputText': text,
                'taskType': 'SINGLE_EMBEDDING',
                'embeddingConfig': {'outputEmbeddingLength': 1024},
            }),
        )
        embedding = json.loads(response['body'].read())['embedding']
        embeddings.append({
            'start_time': scene['start_time'],
            'end_time': scene['end_time'],
            'embedding': embedding,
        })
    return embeddings


def lambda_handler(event, context):
    """Handle VideoUploaded event."""
    import asyncio

    async def _handle():
        detail = event['detail']
        video_id = detail['video_id']
        s3_key = detail['s3_key']

        scenes = await detect_scenes(s3_key)
        captions = await generate_captions(s3_key)
        scene_embeddings = await generate_scene_embeddings(scenes, captions)

        async with get_db_session() as db:
            await db.execute(
                "UPDATE videos SET captions = :captions WHERE id = :id",
                {"captions": captions, "id": video_id},
            )
            for scene_emb in scene_embeddings:
                await db.execute(
                    """INSERT INTO video_scenes
                    (video_id, start_time, end_time, embedding)
                    VALUES (:video_id, :start_time, :end_time, :embedding)""",
                    {
                        "video_id": video_id,
                        "start_time": scene_emb['start_time'],
                        "end_time": scene_emb['end_time'],
                        "embedding": scene_emb['embedding'],
                    },
                )

        events = get_event_service()
        await events.video_processed(video_id, scenes, captions)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'video_id': video_id,
                'scenes_detected': len(scenes),
                'caption_length': len(captions),
            }),
        }

    return asyncio.run(_handle())
