"""Lambda: GET /feed/real/personalized/{userId}"""
import json
import os
import sys
sys.path.insert(0, '/opt/python')

def handler(event, context):
    """Get personalized feed for user"""
    try:
        # Extract userId from path parameters
        user_id = event.get('pathParameters', {}).get('userId')
        
        if not user_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing userId'})
            }
        
        # Get limit from query parameters
        limit = event.get('queryStringParameters', {}).get('limit', '20')
        
        # TODO: Implement personalized feed logic
        # For now, return mock data
        feed_items = [
            {
                'id': f'article-{i}',
                'title': f'Article {i}',
                'category': 'technology',
                'relevance_score': 0.9 - (i * 0.1)
            }
            for i in range(int(limit))
        ]
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'userId': user_id,
                'items': feed_items,
                'count': len(feed_items)
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
