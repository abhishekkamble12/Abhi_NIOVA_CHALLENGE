"""Lambda handler for video processing with Transcribe and Rekognition"""
import json
import os
import sys
sys.path.append('/opt/python')

from services.aws_ai_service import (
    transcribe_audio,
    get_transcription_result,
    detect_video_scenes,
    detect_labels_in_video
)


def handler(event, context):
    """Process video using Transcribe and Rekognition"""
    try:
        # Handle S3 event trigger
        if 'Records' in event:
            record = event['Records'][0]
            s3_bucket = record['s3']['bucket']['name']
            s3_key = record['s3']['object']['key']
        else:
            body = json.loads(event.get('body', '{}'))
            s3_bucket = body.get('bucket')
            s3_key = body.get('key')
        
        if not s3_bucket or not s3_key:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Bucket and key required'})
            }
        
        video_id = s3_key.split('/')[-1].split('.')[0]
        s3_uri = f's3://{s3_bucket}/{s3_key}'
        
        # Start transcription
        transcribe_job = transcribe_audio(
            s3_uri=s3_uri,
            job_name=f'transcribe-{video_id}'
        )
        
        # Detect scenes
        scenes = detect_video_scenes(s3_bucket, s3_key)
        
        # Detect labels/objects
        labels = detect_labels_in_video(s3_bucket, s3_key, max_labels=10)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'video_id': video_id,
                'transcription_job': transcribe_job['job_name'],
                'scenes_detected': len(scenes),
                'scenes': scenes[:5],  # First 5 scenes
                'labels': labels[:10],  # Top 10 labels
                's3_uri': s3_uri
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
