"""Lambda: Start Amazon Transcribe job"""
import json
import boto3
import os
from datetime import datetime

transcribe = boto3.client('transcribe', region_name=os.getenv('AWS_REGION', 'ap-south-1'))


def handler(event, context):
    """Start transcription job for video audio"""
    try:
        # Parse input from Step Functions
        video_id = event.get('videoId')
        s3_uri = event.get('s3Uri')
        
        if not all([video_id, s3_uri]):
            return {
                'statusCode': 400,
                'error': 'Missing required fields: videoId, s3Uri'
            }
        
        # Generate unique job name
        timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
        job_name = f'transcribe-{video_id}-{timestamp}'
        
        # Determine media format from S3 URI
        file_extension = s3_uri.split('.')[-1].lower()
        media_format_map = {
            'mp4': 'mp4',
            'mov': 'mov',
            'avi': 'avi',
            'mkv': 'mkv',
            'webm': 'webm',
            'mp3': 'mp3',
            'wav': 'wav'
        }
        media_format = media_format_map.get(file_extension, 'mp4')
        
        # Start transcription job
        response = transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': s3_uri},
            MediaFormat=media_format,
            LanguageCode='en-US',
            OutputBucketName=os.getenv('S3_BUCKET'),
            Settings={
                'ShowSpeakerLabels': True,
                'MaxSpeakerLabels': 5
            }
        )
        
        # Return job details
        return {
            'statusCode': 200,
            'jobName': job_name,
            'status': 'IN_PROGRESS',
            'videoId': video_id,
            's3Uri': s3_uri,
            'mediaFormat': media_format
        }
        
    except transcribe.exceptions.ConflictException:
        # Job already exists
        return {
            'statusCode': 409,
            'error': f'Transcription job already exists: {job_name}'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'error': str(e)
        }
