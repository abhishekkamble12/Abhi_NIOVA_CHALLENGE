"""Lambda handler demonstrating multi-storage integration - CORRECTED"""
import json
import os
import sys
import asyncio
sys.path.append('/opt/python')

from services.storage_service import (
    log_user_activity,
    store_embedding,
    create_post,
    get_brand
)
from services.aws_ai_service import generate_embeddings, generate_text


async def async_handler(event, context):
    """Async business logic"""
    # Parse body with error handling
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }
    
    # Validate required fields
    user_id = body.get('userId')
    brand_id = body.get('brandId')
    platform = body.get('platform', 'instagram')
    topic = body.get('topic')
    
    if not all([user_id, brand_id, topic]):
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Missing required fields: userId, brandId, topic'})
        }
    
    # 1. Get brand from Aurora
    brand = await get_brand(brand_id)
    if not brand:
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Brand not found'})
        }
    
    # 2. Generate content with Bedrock
    prompt = f"Generate a {platform} post for {brand['name']} about: {topic}"
    content = generate_text(prompt, max_tokens=300)
    
    # 3. Generate embedding with Bedrock Titan
    embedding = generate_embeddings(content)
    
    # 4. Store embedding in OpenSearch
    post_id = f"post-{context.request_id}"
    store_embedding(
        doc_id=post_id,
        embedding=embedding,
        metadata={
            'brandId': brand_id,
            'platform': platform,
            'topic': topic,
            'contentPreview': content[:100]
        },
        index='social-posts'
    )
    
    # 5. Store post in Aurora
    await create_post(
        post_id=post_id,
        brand_id=brand_id,
        platform=platform,
        content=content
    )
    
    # 6. Log activity in DynamoDB
    log_user_activity(
        user_id=user_id,
        activity_type='POST_GENERATED',
        metadata={
            'postId': post_id,
            'brandId': brand_id,
            'platform': platform
        }
    )
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'postId': post_id,
            'content': content,
            'storage': {
                'aurora': 'post metadata',
                'opensearch': 'embedding vector',
                'dynamodb': 'user activity'
            }
        })
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
