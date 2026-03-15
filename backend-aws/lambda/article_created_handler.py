"""
Lambda Handler: Article Created → Generate Embedding → Store Vector → Generate Social Post
===========================================================================================
Uses Amazon Nova models:
  Embeddings → Nova Multimodal Embeddings (invoke_model)
  Text       → Nova 2 Lite (Converse API)
"""
import json
import os
import boto3
from services.aurora_service import get_db_session
from services.cache_service import get_cache_service
from services.event_service import get_event_service

bedrock = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION', 'us-east-1'))

NOVA_EMBEDDING_MODEL = os.getenv('NOVA_EMBEDDING_MODEL', 'amazon.nova-2-multimodal-embeddings-v1:0')
NOVA_TEXT_MODEL = os.getenv('NOVA_TEXT_MODEL', 'amazon.nova-2-lite-v1:0')


async def generate_embedding(text: str) -> list:
    """Generate embedding using Amazon Nova Multimodal Embeddings."""
    response = bedrock.invoke_model(
        modelId=NOVA_EMBEDDING_MODEL,
        body=json.dumps({
            'input': text,
            'inputText': text,
            'taskType': 'SINGLE_EMBEDDING',
            'embeddingConfig': {'outputEmbeddingLength': 1024},
        }),
    )
    return json.loads(response['body'].read())['embedding']


async def generate_social_post(title: str, content: str) -> str:
    """Generate social post using Amazon Nova 2 Lite via Converse API."""
    prompt = (
        f"Create an engaging LinkedIn post based on this article:\n"
        f"Title: {title}\nContent: {content[:500]}"
    )
    response = bedrock.converse(
        modelId=NOVA_TEXT_MODEL,
        messages=[
            {'role': 'user', 'content': [{'text': prompt}]}
        ],
        inferenceConfig={'temperature': 0.7, 'maxTokens': 300},
    )
    return response['output']['message']['content'][0]['text']


def lambda_handler(event, context):
    """Handle ArticleCreated event."""
    import asyncio

    async def _handle():
        detail = event['detail']
        article_id = detail['article_id']
        title = detail['title']
        content = detail['content']

        text = f"{title} {content}"
        embedding = await generate_embedding(text)

        async with get_db_session() as db:
            await db.execute(
                "UPDATE articles SET embedding = :embedding WHERE id = :id",
                {"embedding": embedding, "id": article_id},
            )

        cache = get_cache_service()
        await cache.set_embedding(text, embedding)

        post_content = await generate_social_post(title, content)

        async with get_db_session() as db:
            result = await db.execute(
                "INSERT INTO social_posts (platform, content, source_article_id) "
                "VALUES (:platform, :content, :article_id) RETURNING id",
                {"platform": "linkedin", "content": post_content, "article_id": article_id},
            )
            post_id = result.scalar()

        events = get_event_service()
        await events.post_created(post_id, "linkedin", post_content)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'article_id': article_id,
                'post_id': post_id,
                'embedding_dim': len(embedding),
            }),
        }

    return asyncio.run(_handle())
