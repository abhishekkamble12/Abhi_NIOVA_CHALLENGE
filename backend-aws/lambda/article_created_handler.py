"""Lambda Handler: Article Created → Generate Embedding → Store Vector → Generate Social Post"""
import json
import boto3
from services.aurora_service import get_db_session
from services.cache_service import get_cache_service
from services.event_service import get_event_service

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

async def generate_embedding(text: str) -> list:
    """Generate embedding using Bedrock Titan"""
    response = bedrock.invoke_model(
        modelId='amazon.titan-embed-text-v2:0',
        body=json.dumps({"inputText": text})
    )
    return json.loads(response['body'].read())['embedding']

async def generate_social_post(title: str, content: str) -> str:
    """Generate social post using Bedrock Claude"""
    prompt = f"Create an engaging LinkedIn post based on this article:\nTitle: {title}\nContent: {content[:500]}"
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "messages": [{"role": "user", "content": prompt}]
        })
    )
    return json.loads(response['body'].read())['content'][0]['text']

def lambda_handler(event, context):
    """Handle ArticleCreated event"""
    detail = event['detail']
    article_id = detail['article_id']
    title = detail['title']
    content = detail['content']
    
    # Generate embedding
    text = f"{title} {content}"
    embedding = await generate_embedding(text)
    
    # Store vector in Aurora
    async with get_db_session() as db:
        await db.execute(
            "UPDATE articles SET embedding = :embedding WHERE id = :id",
            {"embedding": embedding, "id": article_id}
        )
    
    # Cache embedding
    cache = get_cache_service()
    await cache.set_embedding(text, embedding)
    
    # Generate social post
    post_content = await generate_social_post(title, content)
    
    # Store post
    async with get_db_session() as db:
        result = await db.execute(
            "INSERT INTO social_posts (platform, content, source_article_id) VALUES (:platform, :content, :article_id) RETURNING id",
            {"platform": "linkedin", "content": post_content, "article_id": article_id}
        )
        post_id = result.scalar()
    
    # Publish PostCreated event
    events = get_event_service()
    await events.post_created(post_id, "linkedin", post_content)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'article_id': article_id,
            'post_id': post_id,
            'embedding_dim': len(embedding)
        })
    }
