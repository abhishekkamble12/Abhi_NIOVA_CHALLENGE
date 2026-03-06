"""Lambda Handler: Post Engagement → Analyze Performance → Update Learning Model"""
import json
import boto3
from services.aurora_service import get_db_session
from services.cache_service import get_cache_service

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

async def analyze_performance(post_id: int, likes: int, comments: int, shares: int) -> dict:
    """Analyze post performance and extract insights"""
    async with get_db_session() as db:
        result = await db.execute(
            "SELECT content, platform FROM social_posts WHERE id = :id",
            {"id": post_id}
        )
        row = result.fetchone()
    
    engagement_score = (likes * 1) + (comments * 3) + (shares * 5)
    
    # Use Bedrock to analyze what made the post successful
    prompt = f"""Analyze this social media post performance:
Platform: {row['platform']}
Content: {row['content']}
Likes: {likes}, Comments: {comments}, Shares: {shares}
Engagement Score: {engagement_score}

Extract key success factors (tone, hooks, emojis, structure)."""
    
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}]
        })
    )
    insights = json.loads(response['body'].read())['content'][0]['text']
    
    return {
        'engagement_score': engagement_score,
        'insights': insights,
        'performance_tier': 'high' if engagement_score > 500 else 'medium' if engagement_score > 100 else 'low'
    }

def lambda_handler(event, context):
    """Handle PostEngagement event"""
    detail = event['detail']
    post_id = detail['post_id']
    likes = detail['likes']
    comments = detail['comments']
    shares = detail['shares']
    
    # Analyze performance
    analysis = await analyze_performance(post_id, likes, comments, shares)
    
    # Store learning insights
    async with get_db_session() as db:
        await db.execute(
            """INSERT INTO performance_insights 
            (post_id, engagement_score, insights, performance_tier) 
            VALUES (:post_id, :score, :insights, :tier)""",
            {
                "post_id": post_id,
                "score": analysis['engagement_score'],
                "insights": analysis['insights'],
                "tier": analysis['performance_tier']
            }
        )
    
    # Cache insights for future content generation
    cache = get_cache_service()
    await cache.set(f"insights:{post_id}", analysis, ttl=86400)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'post_id': post_id,
            'engagement_score': analysis['engagement_score'],
            'performance_tier': analysis['performance_tier']
        })
    }
