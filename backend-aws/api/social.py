"""Social Media API Endpoints"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.aurora_service import get_db_connection
from services.bedrock_service import get_bedrock_service
from services.cache_service import get_cache_service
from services.event_service import get_event_service

router = APIRouter()

class BrandCreate(BaseModel):
    name: str
    industry: str
    tone: str
    target_audience: str

class PostGenerate(BaseModel):
    brand_id: int
    platform: str

@router.post("/brands")
async def create_brand(brand: BrandCreate):
    """Create a new brand"""
    async with get_db_connection() as conn:
        brand_id = await conn.fetchval(
            """INSERT INTO brands (name, industry, tone, target_audience) 
            VALUES ($1, $2, $3, $4) RETURNING id""",
            brand.name, brand.industry, brand.tone, brand.target_audience
        )
    return {"id": brand_id, **brand.dict()}

@router.get("/brands/{brand_id}")
async def get_brand(brand_id: int):
    """Get brand by ID"""
    async with get_db_connection() as conn:
        brand = await conn.fetchrow("SELECT * FROM brands WHERE id = $1", brand_id)
    if not brand:
        raise HTTPException(404, "Brand not found")
    return dict(brand)

@router.get("/brands")
async def list_brands():
    """List all brands"""
    async with get_db_connection() as conn:
        brands = await conn.fetch("SELECT * FROM brands ORDER BY id DESC")
    return [dict(b) for b in brands]

@router.post("/generate/content")
async def generate_content(brand_id: int, platform: str):
    """Generate social media content"""
    # Get brand
    async with get_db_connection() as conn:
        brand = await conn.fetchrow("SELECT * FROM brands WHERE id = $1", brand_id)
    
    if not brand:
        raise HTTPException(404, "Brand not found")
    
    # Generate content with Bedrock
    bedrock = get_bedrock_service()
    prompt = f"Create a {platform} post for {brand['name']} ({brand['industry']}). Tone: {brand['tone']}. Target: {brand['target_audience']}."
    content = await bedrock.generate_text(prompt, max_tokens=300)
    
    # Save post
    async with get_db_connection() as conn:
        post_id = await conn.fetchval(
            """INSERT INTO social_posts (brand_id, platform, content, status) 
            VALUES ($1, $2, $3, 'draft') RETURNING id""",
            brand_id, platform, content
        )
    
    # Publish event
    events = get_event_service()
    await events.post_created(post_id, platform, content)
    
    return {"id": post_id, "content": content, "platform": platform}

@router.get("/posts/{post_id}")
async def get_post(post_id: int):
    """Get post by ID"""
    async with get_db_connection() as conn:
        post = await conn.fetchrow("SELECT * FROM social_posts WHERE id = $1", post_id)
    if not post:
        raise HTTPException(404, "Post not found")
    return dict(post)

@router.get("/brand/{brand_id}/posts")
async def get_brand_posts(brand_id: int):
    """Get all posts for a brand"""
    async with get_db_connection() as conn:
        posts = await conn.fetch(
            "SELECT * FROM social_posts WHERE brand_id = $1 ORDER BY created_at DESC",
            brand_id
        )
    return [dict(p) for p in posts]

@router.put("/posts/{post_id}/publish")
async def publish_post(post_id: int):
    """Publish a post"""
    async with get_db_connection() as conn:
        await conn.execute(
            "UPDATE social_posts SET status = 'published', published_at = NOW() WHERE id = $1",
            post_id
        )
    return {"status": "published"}

@router.post("/track/engagement/{post_id}")
async def track_engagement(post_id: int, likes: int, comments: int, shares: int, impressions: int = 0, ctr: float = 0.0):
    """Track post engagement"""
    async with get_db_connection() as conn:
        await conn.execute(
            """INSERT INTO post_engagement (post_id, likes, comments, shares, impressions, ctr) 
            VALUES ($1, $2, $3, $4, $5, $6)""",
            post_id, likes, comments, shares, impressions, ctr
        )
    
    # Publish event
    events = get_event_service()
    await events.publish_event('PostEngagement', {
        'post_id': post_id,
        'likes': likes,
        'comments': comments,
        'shares': shares
    })
    
    return {"status": "tracked"}

@router.get("/analytics/brand/{brand_id}")
async def get_analytics(brand_id: int):
    """Get brand analytics"""
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
