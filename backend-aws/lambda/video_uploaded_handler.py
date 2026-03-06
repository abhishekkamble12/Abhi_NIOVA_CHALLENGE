"""Lambda Handler: Video Uploaded → Detect Scenes → Generate Captions → Store Embeddings"""
import json
import boto3
from services.aurora_service import get_db_session
from services.s3_service import get_s3_service
from services.event_service import get_event_service

rekognition = boto3.client('rekognition', region_name='us-east-1')
transcribe = boto3.client('transcribe', region_name='us-east-1')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

async def detect_scenes(s3_key: str) -> list:
    """Detect scenes using Rekognition"""
    response = rekognition.start_segment_detection(
        Video={'S3Object': {'Bucket': 'hivemind-media', 'Name': s3_key}},
        SegmentTypes=['SHOT']
    )
    job_id = response['JobId']
    
    # Wait for completion (simplified)
    result = rekognition.get_segment_detection(JobId=job_id)
    return [
        {
            'start_time': seg['StartTimestampMillis'] / 1000,
            'end_time': seg['EndTimestampMillis'] / 1000,
            'confidence': seg['ShotSegment']['Confidence']
        }
        for seg in result['Segments']
    ]

async def generate_captions(s3_key: str) -> str:
    """Generate captions using Transcribe"""
    job_name = f"transcribe-{s3_key.replace('/', '-')}"
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': f"s3://hivemind-media/{s3_key}"},
        MediaFormat='mp4',
        LanguageCode='en-US'
    )
    
    # Wait for completion (simplified)
    result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    transcript_uri = result['TranscriptionJob']['Transcript']['TranscriptFileUri']
    
    # Download transcript
    import urllib.request
    with urllib.request.urlopen(transcript_uri) as response:
        transcript = json.loads(response.read())
    
    return transcript['results']['transcripts'][0]['transcript']

async def generate_scene_embeddings(scenes: list, captions: str) -> list:
    """Generate embeddings for each scene"""
    embeddings = []
    for scene in scenes:
        text = f"Scene {scene['start_time']}-{scene['end_time']}: {captions}"
        response = bedrock.invoke_model(
            modelId='amazon.titan-embed-text-v2:0',
            body=json.dumps({"inputText": text})
        )
        embedding = json.loads(response['body'].read())['embedding']
        embeddings.append({
            'start_time': scene['start_time'],
            'end_time': scene['end_time'],
            'embedding': embedding
        })
    return embeddings

def lambda_handler(event, context):
    """Handle VideoUploaded event"""
    detail = event['detail']
    video_id = detail['video_id']
    s3_key = detail['s3_key']
    
    # Detect scenes
    scenes = await detect_scenes(s3_key)
    
    # Generate captions
    captions = await generate_captions(s3_key)
    
    # Generate embeddings
    scene_embeddings = await generate_scene_embeddings(scenes, captions)
    
    # Store in Aurora
    async with get_db_session() as db:
        await db.execute(
            "UPDATE videos SET captions = :captions WHERE id = :id",
            {"captions": captions, "id": video_id}
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
                    "embedding": scene_emb['embedding']
                }
            )
    
    # Publish VideoProcessed event
    events = get_event_service()
    await events.video_processed(video_id, scenes, captions)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'video_id': video_id,
            'scenes_detected': len(scenes),
            'caption_length': len(captions)
        })
    }
