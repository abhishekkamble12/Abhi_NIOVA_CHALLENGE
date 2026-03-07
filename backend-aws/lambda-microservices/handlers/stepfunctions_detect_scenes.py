"""Lambda: Detect scenes using Amazon Rekognition"""
import json
import boto3
import os

rekognition = boto3.client('rekognition', region_name=os.getenv('AWS_REGION', 'ap-south-1'))


def handler(event, context):
    """Start scene detection job (non-blocking)"""
    try:
        # Parse input from Step Functions
        video_id = event.get('videoId')
        s3_bucket = event.get('s3Bucket')
        s3_key = event.get('s3Key')
        
        if not all([video_id, s3_bucket, s3_key]):
            return {
                'statusCode': 400,
                'error': 'Missing required fields: videoId, s3Bucket, s3Key'
            }
        
        # Start segment detection (scenes)
        response = rekognition.start_segment_detection(
            Video={
                'S3Object': {
                    'Bucket': s3_bucket,
                    'Name': s3_key
                }
            },
            SegmentTypes=['SHOT', 'TECHNICAL_CUE'],
            NotificationChannel={
                'SNSTopicArn': os.getenv('SNS_TOPIC_ARN', ''),
                'RoleArn': os.getenv('REKOGNITION_ROLE_ARN', '')
            } if os.getenv('SNS_TOPIC_ARN') else None
        )
        
        job_id = response['JobId']
        
        # Return job details
        return {
            'statusCode': 200,
            'jobId': job_id,
            'videoId': video_id,
            's3Bucket': s3_bucket,
            's3Key': s3_key,
            'status': 'IN_PROGRESS'
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'error': str(e)
        }


def get_scene_results(job_id):
    """Get scene detection results (called by Step Functions after polling)"""
    try:
        response = rekognition.get_segment_detection(JobId=job_id)
        
        status = response['JobStatus']
        
        if status == 'SUCCEEDED':
            scenes = []
            for segment in response.get('Segments', []):
                if segment['Type'] == 'SHOT':
                    scenes.append({
                        'startTime': segment['StartTimestampMillis'] / 1000,
                        'endTime': segment['EndTimestampMillis'] / 1000,
                        'confidence': segment['ShotSegment']['Confidence'],
                        'index': segment['ShotSegment']['Index']
                    })
            
            return {
                'statusCode': 200,
                'status': 'COMPLETED',
                'scenes': scenes,
                'sceneCount': len(scenes)
            }
        elif status == 'FAILED':
            return {
                'statusCode': 500,
                'status': 'FAILED',
                'error': response.get('StatusMessage', 'Unknown error')
            }
        else:
            return {
                'statusCode': 200,
                'status': status,
                'scenes': []
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'error': str(e)
        }
