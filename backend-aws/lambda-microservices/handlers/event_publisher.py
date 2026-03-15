"""EventBridge event publisher"""
import json
import os
import boto3
from datetime import datetime
from typing import Dict, Any

events = boto3.client('events', region_name=os.getenv('AWS_REGION', 'ap-south-1'))
EVENT_BUS = os.getenv('EVENT_BUS_NAME', 'hivemind-bus')


def publish_event(source: str, detail_type: str, detail: Dict[str, Any]) -> Dict[str, Any]:
    """Publish event to EventBridge"""
    response = events.put_events(
        Entries=[{
            'Source': source,
            'DetailType': detail_type,
            'Detail': json.dumps(detail),
            'EventBusName': EVENT_BUS,
            'Time': datetime.utcnow()
        }]
    )
    return response


def video_uploaded_handler(event, context):
    """Publish VideoUploaded event"""
    record = event['Records'][0]
    s3_bucket = record['s3']['bucket']['name']
    s3_key = record['s3']['object']['key']
    
    video_id = s3_key.split('/')[-1].split('.')[0]
    
    publish_event(
        source='hivemind.video',
        detail_type='VideoUploaded',
        detail={
            'videoId': video_id,
            's3Bucket': s3_bucket,
            's3Key': s3_key,
            'userId': event.get('userId', 'system'),
            'fileSize': record['s3']['object']['size']
        }
    )
    
    return {'statusCode': 200, 'body': json.dumps({'videoId': video_id})}


def post_generated_handler(event, context):
    """Publish PostGenerated event"""
    body = json.loads(event.get('body', '{}'))
    
    publish_event(
        source='hivemind.social',
        detail_type='PostGenerated',
        detail={
            'postId': body['postId'],
            'brandId': body['brandId'],
            'platform': body['platform'],
            'content': body['content'],
            'generatedBy': 'bedrock-nova'
        }
    )
    
    return {'statusCode': 200, 'body': json.dumps({'published': True})}


def article_read_handler(event, context):
    """Publish ArticleRead event"""
    body = json.loads(event.get('body', '{}'))
    
    publish_event(
        source='hivemind.news',
        detail_type='ArticleRead',
        detail={
            'articleId': body['articleId'],
            'userId': body['userId'],
            'readDuration': body.get('readDuration', 0),
            'scrollDepth': body.get('scrollDepth', 0),
            'category': body.get('category', 'general')
        }
    )
    
    return {'statusCode': 200, 'body': json.dumps({'tracked': True})}


def engagement_tracked_handler(event, context):
    """Publish EngagementTracked event"""
    body = json.loads(event.get('body', '{}'))
    
    publish_event(
        source='hivemind.social',
        detail_type='EngagementTracked',
        detail={
            'postId': body['postId'],
            'platform': body['platform'],
            'engagementType': body['engagementType'],
            'count': body['count'],
            'timestamp': datetime.utcnow().isoformat()
        }
    )
    
    return {'statusCode': 200, 'body': json.dumps({'tracked': True})}
