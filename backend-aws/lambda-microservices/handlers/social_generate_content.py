"""Lambda: POST /api/v1/social/generate/content - CORRECTED"""
import asyncio
import json
import sys
import os
sys.path.insert(0, '/opt/python')
sys.path.insert(0, os.path.dirname(__file__))

from services.social_service import generate_content_logic


async def async_handler(event, context):
    """Async business logic"""
    # Extract query parameters
    query_params = event.get('queryStringParameters') or {}
    brand_id = query_params.get('brand_id')
    platform = query_params.get('platform')
    
    if not brand_id or not platform:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Missing required query parameters: brand_id, platform'})
        }
    
    # Validate brand_id is numeric
    try:
        brand_id_int = int(brand_id)
    except ValueError:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'brand_id must be a number'})
        }
    
    # Execute business logic
    result = await generate_content_logic(brand_id_int, platform)
    
    if not result:
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Brand not found'})
        }
    
    return {
        'statusCode': 201,
        'headers': {
                'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(result)
    }


def handler(event, context):
    """Synchronous Lambda entrypoint"""
    try:
        return asyncio.run(async_handler(event, context))
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
