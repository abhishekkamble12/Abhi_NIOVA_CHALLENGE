"""Lambda handler demonstrating multi-storage integration"""
import json
import os
import sys
sys.path.append('/opt/python')

from services.storage_service import (
    upload_video_to_s3,
    log_user_activity,
    store_embedding,
    create_post,
    get_brand
)
from services.aws_ai_service import generate_embeddings, generate_text


async def handler(event, context):
    """
    Complete workflow:
    1. Generate content with Bedrock
    2. Store embedding in OpenSearch
    3. Store post in Aurora
    4. Log activity in DynamoDB
    """
    try:
        body = json.loads(event.get('body', '{}'))
        
        user_id = body.get('userId')
        brand_id = body.get('brandId')
        platform = body.get('platform', 'instagram')
        topic = body.get('topic')
        
        # 1. Get brand from Aurora
        brand = await get_brand(brand_id)
        if not brand:
            return {'statusCode': 404, 'body': json.dumps({'error': 'Brand not found'})}
        
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
            'headers': {'Content-Type': 'application/json'},
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
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
