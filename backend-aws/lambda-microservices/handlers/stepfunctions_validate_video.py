"""Lambda: Validate video file before processing"""
import json
import boto3
import os

s3 = boto3.client('s3', region_name=os.getenv('AWS_REGION', 'ap-south-1'))

# Supported video formats
SUPPORTED_FORMATS = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # 5GB


def handler(event, context):
    """Validate video file exists and meets requirements"""
    try:
        # Parse input from Step Functions
        video_id = event.get('videoId')
        s3_bucket = event.get('s3Bucket')
        s3_key = event.get('s3Key')
        
        if not all([video_id, s3_bucket, s3_key]):
            return {
                'statusCode': 400,
                'valid': False,
                'error': 'Missing required fields: videoId, s3Bucket, s3Key'
            }
        
        # Check if file exists
        try:
            response = s3.head_object(Bucket=s3_bucket, Key=s3_key)
        except s3.exceptions.NoSuchKey:
            return {
                'statusCode': 404,
                'valid': False,
                'error': f'Video file not found: s3://{s3_bucket}/{s3_key}'
            }
        
        # Get file metadata
        file_size = response['ContentLength']
        content_type = response.get('ContentType', '')
        
        # Validate file size
        if file_size > MAX_FILE_SIZE:
            return {
                'statusCode': 400,
                'valid': False,
                'error': f'File size {file_size} exceeds maximum {MAX_FILE_SIZE}'
            }
        
        # Validate file format
        file_extension = os.path.splitext(s3_key)[1].lower()
        if file_extension not in SUPPORTED_FORMATS:
            return {
                'statusCode': 400,
                'valid': False,
                'error': f'Unsupported format {file_extension}. Supported: {SUPPORTED_FORMATS}'
            }
        
        # Return validation result
        return {
            'statusCode': 200,
            'valid': True,
            'videoId': video_id,
            's3Bucket': s3_bucket,
            's3Key': s3_key,
            'fileSize': file_size,
            'contentType': content_type,
            'format': file_extension
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'valid': False,
            'error': str(e)
        }
