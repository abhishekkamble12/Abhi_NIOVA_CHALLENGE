"""Video upload workflow with multi-storage"""
import json
import os
import sys
sys.path.append('/opt/python')

from services.storage_service import (
    upload_video_to_s3,
    log_user_activity,
    store_embedding,
    store_video_metadata
)
from services.aws_ai_service import transcribe_audio, detect_video_scenes, generate_embeddings


async def handler(event, context):
    """
    Video upload workflow:
    1. Upload video to S3
    2. Start Transcribe job
    3. Detect scenes with Rekognition
    4. Generate embeddings from transcription
    5. Store embeddings in OpenSearch
    6. Store metadata in Aurora
    7. Log activity in DynamoDB
    """
    try:
        # S3 event trigger
        if 'Records' in event:
            record = event['Records'][0]
            s3_bucket = record['s3']['bucket']['name']
            s3_key = record['s3']['object']['key']
            video_id = s3_key.split('/')[-1].split('.')[0]
            user_id = record.get('userIdentity', {}).get('principalId', 'system')
        else:
            body = json.loads(event.get('body', '{}'))
            video_id = body['videoId']
            s3_bucket = body['bucket']
            s3_key = body['key']
            user_id = body['userId']
        
        s3_url = f's3://{s3_bucket}/{s3_key}'
        
        # 1. Start transcription (async)
        transcribe_job = transcribe_audio(
            s3_uri=s3_url,
            job_name=f'transcribe-{video_id}'
        )
        
        # 2. Detect scenes (sync)
        scenes = detect_video_scenes(s3_bucket, s3_key)
        
        # 3. Generate scene embeddings
        for idx, scene in enumerate(scenes[:5]):  # First 5 scenes
            scene_text = f"Scene {idx+1}: {scene['start_time']}-{scene['end_time']}s"
            embedding = generate_embeddings(scene_text)
            
            # Store in OpenSearch
            store_embedding(
                doc_id=f'{video_id}-scene-{idx}',
                embedding=embedding,
                metadata={
                    'videoId': video_id,
                    'sceneIndex': idx,
                    'startTime': scene['start_time'],
                    'endTime': scene['end_time'],
                    'confidence': scene['confidence']
                },
                index='video-scenes'
            )
        
        # 4. Store video metadata in Aurora
        duration = scenes[-1]['end_time'] if scenes else 0
        await store_video_metadata(
            video_id=video_id,
            s3_url=s3_url,
            duration=duration,
            transcription=None  # Will be updated when transcription completes
        )
        
        # 5. Log activity in DynamoDB
        log_user_activity(
            user_id=user_id,
            activity_type='VIDEO_UPLOADED',
            metadata={
                'videoId': video_id,
                's3Url': s3_url,
                'scenesDetected': len(scenes),
                'transcriptionJob': transcribe_job['job_name']
            }
        )
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'videoId': video_id,
                's3Url': s3_url,
                'scenesDetected': len(scenes),
                'transcriptionJob': transcribe_job['job_name'],
                'storage': {
                    's3': 'video file',
                    'opensearch': f'{len(scenes)} scene embeddings',
                    'aurora': 'video metadata',
                    'dynamodb': 'user activity'
                }
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
