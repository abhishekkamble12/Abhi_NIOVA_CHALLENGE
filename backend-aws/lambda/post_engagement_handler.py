"""
Lambda Handler: Post Engagement → Analyze Performance → Update Learning Model
===============================================================================
Uses Amazon Nova 2 Lite via the Converse API for performance analysis.
"""
import json
import os
import boto3
from services.aurora_service import get_db_session
from services.cache_service import get_cache_service

bedrock = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION', 'us-east-1'))

NOVA_TEXT_MODEL = os.getenv('NOVA_TEXT_MODEL', 'amazon.nova-2-lite-v1:0')


async def analyze_performance(
    post_id: int, likes: int, comments: int, shares: int
) -> dict:
    """Analyze post performance and extract insights using Nova 2 Lite."""
    async with get_db_session() as db:
        result = await db.execute(
            "SELECT content, platform FROM social_posts WHERE id = :id",
            {"id": post_id},
        )
        row = result.fetchone()

    engagement_score = (likes * 1) + (comments * 3) + (shares * 5)

    prompt = f"""Analyze this social media post performance:
Platform: {row['platform']}
Content: {row['content']}
Likes: {likes}, Comments: {comments}, Shares: {shares}
Engagement Score: {engagement_score}

Extract key success factors (tone, hooks, emojis, structure)."""

    response = bedrock.converse(
        modelId=NOVA_TEXT_MODEL,
        messages=[
            {'role': 'user', 'content': [{'text': prompt}]}
        ],
        inferenceConfig={'temperature': 0.5, 'maxTokens': 500},
    )
    insights = response['output']['message']['content'][0]['text']

    return {
        'engagement_score': engagement_score,
        'insights': insights,
        'performance_tier': (
            'high' if engagement_score > 500
            else 'medium' if engagement_score > 100
            else 'low'
        ),
    }


def lambda_handler(event, context):
    """Handle PostEngagement event."""
    import asyncio

    async def _handle():
        detail = event['detail']
        post_id = detail['post_id']
        likes = detail['likes']
        comments = detail['comments']
        shares = detail['shares']

        analysis = await analyze_performance(post_id, likes, comments, shares)

        async with get_db_session() as db:
            await db.execute(
                """INSERT INTO performance_insights
                (post_id, engagement_score, insights, performance_tier)
                VALUES (:post_id, :score, :insights, :tier)""",
                {
                    "post_id": post_id,
                    "score": analysis['engagement_score'],
                    "insights": analysis['insights'],
                    "tier": analysis['performance_tier'],
                },
            )

        cache = get_cache_service()
        await cache.set(f"insights:{post_id}", analysis, ttl=86400)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'post_id': post_id,
                'engagement_score': analysis['engagement_score'],
                'performance_tier': analysis['performance_tier'],
            }),
        }

    return asyncio.run(_handle())
