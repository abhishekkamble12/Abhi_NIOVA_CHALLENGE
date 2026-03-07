"""Lambda: Detect labels/objects using Amazon Rekognition"""
import json
import boto3
import os

rekognition = boto3.client('rekognition', region_name=os.getenv('AWS_REGION', 'ap-south-1'))


def handler(event, context):
    """Start label detection job (non-blocking)"""
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
        
        # Start label detection
        response = rekognition.start_label_detection(
            Video={
                'S3Object': {
                    'Bucket': s3_bucket,
                    'Name': s3_key
                }
            },
            MinConfidence=70.0,
            Features=['GENERAL_LABELS'],
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


def get_label_results(job_id, max_results=50):
    """Get label detection results (called by Step Functions after polling)"""
    try:
        response = rekognition.get_label_detection(
            JobId=job_id,
            MaxResults=max_results,
            SortBy='TIMESTAMP'
        )
        
        status = response['JobStatus']
        
        if status == 'SUCCEEDED':
            # Aggregate labels by name
            label_map = {}
            for label_detection in response.get('Labels', []):
                label = label_detection['Label']
                label_name = label['Name']
                
                if label_name not in label_map:
                    label_map[label_name] = {
                        'name': label_name,
                        'confidence': label['Confidence'],
                        'instances': [],
                        'timestamps': []
                    }
                
                label_map[label_name]['timestamps'].append(
                    label_detection['Timestamp'] / 1000
                )
                
                # Add instances (bounding boxes)
                for instance in label.get('Instances', []):
                    if instance.get('BoundingBox'):
                        label_map[label_name]['instances'].append({
                            'boundingBox': instance['BoundingBox'],
                            'confidence': instance['Confidence']
                        })
            
            # Convert to list and sort by confidence
            labels = sorted(
                label_map.values(),
                key=lambda x: x['confidence'],
                reverse=True
            )
            
            return {
                'statusCode': 200,
                'status': 'COMPLETED',
                'labels': labels[:max_results],
                'labelCount': len(labels)
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
                'labels': []
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'error': str(e)
        }
