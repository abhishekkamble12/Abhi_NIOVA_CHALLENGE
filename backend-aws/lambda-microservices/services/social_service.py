"""Business logic for social media operations"""
import asyncio
from services.aurora_service import get_db_connection
from services.bedrock_service import get_bedrock_service
from services.event_service import get_event_service

async def create_brand_logic(name: str, industry: str, tone: str, target_audience: str):
    """Create brand business logic"""
    async with get_db_connection() as conn:
        brand_id = await conn.fetchval(
            """INSERT INTO brands (name, industry, tone, target_audience) 
            VALUES ($1, $2, $3, $4) RETURNING id""",
            name, industry, tone, target_audience
        )
    return {"id": brand_id, "name": name, "industry": industry, "tone": tone, "target_audience": target_audience}

async def get_brand_logic(brand_id: int):
    """Get brand business logic"""
    async with get_db_connection() as conn:
        brand = await conn.fetchrow("SELECT * FROM brands WHERE id = $1", brand_id)
    if not brand:
        return None
    return dict(brand)

async def list_brands_logic():
    """List brands business logic"""
    async with get_db_connection() as conn:
        brands = await conn.fetch("SELECT * FROM brands ORDER BY id DESC")
    return [dict(b) for b in brands]

async def generate_content_logic(brand_id: int, platform: str):
    """Generate content business logic"""
    async with get_db_connection() as conn:
        brand = await conn.fetchrow("SELECT * FROM brands WHERE id = $1", brand_id)
    
    if not brand:
        return None
    
    bedrock = get_bedrock_service()
    prompt = f"Create a {platform} post for {brand['name']} ({brand['industry']}). Tone: {brand['tone']}. Target: {brand['target_audience']}."
    content = await bedrock.generate_text(prompt, max_tokens=300)
    
    async with get_db_connection() as conn:
        post_id = await conn.fetchval(
            """INSERT INTO social_posts (brand_id, platform, content, status) 
            VALUES ($1, $2, $3, 'draft') RETURNING id""",
            brand_id, platform, content
        )
    
    events = get_event_service()
    await events.post_created(post_id, platform, content)
    
    return {"id": post_id, "content": content, "platform": platform}

async def get_post_logic(post_id: int):
    """Get post business logic"""
    async with get_db_connection() as conn:
        post = await conn.fetchrow("SELECT * FROM social_posts WHERE id = $1", post_id)
    if not post:
        return None
    return dict(post)

async def get_brand_posts_logic(brand_id: int):
    """Get brand posts business logic"""
    async with get_db_connection() as conn:
        posts = await conn.fetch(
            "SELECT * FROM social_posts WHERE brand_id = $1 ORDER BY created_at DESC",
            brand_id
        )
    return [dict(p) for p in posts]

async def publish_post_logic(post_id: int):
    """Publish post business logic"""
    async with get_db_connection() as conn:
        await conn.execute(
            "UPDATE social_posts SET status = 'published', published_at = NOW() WHERE id = $1",
            post_id
        )
    return {"status": "published"}

async def track_engagement_logic(post_id: int, likes: int, comments: int, shares: int, impressions: int, ctr: float):
    """Track engagement business logic"""
    async with get_db_connection() as conn:
        await conn.execute(
            """INSERT INTO post_engagement (post_id, likes, comments, shares, impressions, ctr) 
            VALUES ($1, $2, $3, $4, $5, $6)""",
            post_id, likes, comments, shares, impressions, ctr
        )
    
    events = get_event_service()
    await events.publish_event('PostEngagement', {
        'post_id': post_id,
        'likes': likes,
        'comments': comments,
        'shares': shares
    })
    
    return {"status": "tracked"}

async def get_analytics_logic(brand_id: int):
    """Get analytics business logic"""
    async with get_db_connection() as conn:
        analytics = await conn.fetchrow(
            """SELECT 
                COUNT(*) as total_posts,
                SUM(e.likes) as total_likes,
                SUM(e.comments) as total_comments,
                SUM(e.shares) as total_shares
            FROM social_posts p
            LEFT JOIN post_engagement e ON p.id = e.post_id
            WHERE p.brand_id = $1""",
            brand_id
        )
    return dict(analytics) if analytics else {}
