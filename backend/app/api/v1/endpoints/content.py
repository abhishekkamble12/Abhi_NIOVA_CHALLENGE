from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional

from app.core.database import get_db
from app.core.redis import redis_client
from app.models.content import Content, Campaign, SocialPost
from app.schemas.content import (
    ContentCreate, ContentUpdate, ContentResponse,
    CampaignCreate, CampaignResponse,
    SocialPostCreate, SocialPostResponse
)

router = APIRouter()

# Content endpoints
@router.get("/", response_model=List[ContentResponse])
async def get_content(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    content_type: Optional[str] = None,
    category: Optional[str] = None,
    featured_only: bool = False,
    published_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Get content with optional filtering"""
    
    cache_key = f"content:list:{skip}:{limit}:{content_type}:{category}:{featured_only}:{published_only}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return cached_data
    
    query = select(Content)
    
    if content_type:
        query = query.where(Content.content_type == content_type)
    
    if category:
        query = query.where(Content.category == category)
    
    if featured_only:
        query = query.where(Content.is_featured == True)
    
    if published_only:
        query = query.where(Content.status == "published")
    
    query = query.order_by(desc(Content.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    content_items = result.scalars().all()
    
    content_responses = [ContentResponse.from_orm(item) for item in content_items]
    
    # Cache for 10 minutes
    await redis_client.set(cache_key, content_responses, expire=600)
    
    return content_responses

@router.get("/featured", response_model=List[ContentResponse])
async def get_featured_content(
    limit: int = Query(6, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Get featured content for homepage"""
    
    cache_key = f"content:featured:{limit}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return cached_data
    
    result = await db.execute(
        select(Content)
        .where(Content.is_featured == True)
        .where(Content.status == "published")
        .order_by(desc(Content.published_at))
        .limit(limit)
    )
    content_items = result.scalars().all()
    
    content_responses = [ContentResponse.from_orm(item) for item in content_items]
    
    # Cache for 15 minutes
    await redis_client.set(cache_key, content_responses, expire=900)
    
    return content_responses

@router.get("/categories", response_model=List[str])
async def get_content_categories(db: AsyncSession = Depends(get_db)):
    """Get all content categories"""
    
    cached_data = await redis_client.get("content:categories")
    if cached_data:
        return cached_data
    
    result = await db.execute(
        select(Content.category)
        .where(Content.category.isnot(None))
        .distinct()
    )
    categories = [row[0] for row in result.fetchall()]
    
    # Cache for 1 hour
    await redis_client.set("content:categories", categories, expire=3600)
    
    return categories

@router.get("/{content_id}", response_model=ContentResponse)
async def get_content_item(content_id: int, db: AsyncSession = Depends(get_db)):
    """Get specific content item by ID"""
    
    cache_key = f"content:{content_id}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return cached_data
    
    result = await db.execute(select(Content).where(Content.id == content_id))
    content_item = result.scalar_one_or_none()
    
    if not content_item:
        raise HTTPException(status_code=404, detail="Content not found")
    
    content_response = ContentResponse.from_orm(content_item)
    
    # Cache for 30 minutes
    await redis_client.set(cache_key, content_response, expire=1800)
    
    return content_response

@router.post("/", response_model=ContentResponse)
async def create_content(content_data: ContentCreate, db: AsyncSession = Depends(get_db)):
    """Create new content"""
    
    db_content = Content(**content_data.dict())
    db.add(db_content)
    await db.commit()
    await db.refresh(db_content)
    
    # Clear related caches
    await redis_client.delete("content:featured:*")
    await redis_client.delete("content:categories")
    
    return ContentResponse.from_orm(db_content)

# Campaign endpoints
@router.get("/campaigns/", response_model=List[CampaignResponse])
async def get_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    campaign_type: Optional[str] = None,
    status: Optional[str] = None,
    featured_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Get campaigns with optional filtering"""
    
    cache_key = f"campaigns:list:{skip}:{limit}:{campaign_type}:{status}:{featured_only}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return cached_data
    
    query = select(Campaign)
    
    if campaign_type:
        query = query.where(Campaign.campaign_type == campaign_type)
    
    if status:
        query = query.where(Campaign.status == status)
    
    if featured_only:
        query = query.where(Campaign.is_featured == True)
    
    query = query.order_by(desc(Campaign.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    campaigns = result.scalars().all()
    
    campaign_responses = [CampaignResponse.from_orm(campaign) for campaign in campaigns]
    
    # Cache for 15 minutes
    await redis_client.set(cache_key, campaign_responses, expire=900)
    
    return campaign_responses

@router.get("/campaigns/featured", response_model=List[CampaignResponse])
async def get_featured_campaigns(
    limit: int = Query(3, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    """Get featured campaigns"""
    
    cache_key = f"campaigns:featured:{limit}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return cached_data
    
    result = await db.execute(
        select(Campaign)
        .where(Campaign.is_featured == True)
        .order_by(desc(Campaign.created_at))
        .limit(limit)
    )
    campaigns = result.scalars().all()
    
    campaign_responses = [CampaignResponse.from_orm(campaign) for campaign in campaigns]
    
    # Cache for 20 minutes
    await redis_client.set(cache_key, campaign_responses, expire=1200)
    
    return campaign_responses

@router.post("/campaigns/", response_model=CampaignResponse)
async def create_campaign(campaign_data: CampaignCreate, db: AsyncSession = Depends(get_db)):
    """Create new campaign"""
    
    db_campaign = Campaign(**campaign_data.dict())
    db.add(db_campaign)
    await db.commit()
    await db.refresh(db_campaign)
    
    # Clear related caches
    await redis_client.delete("campaigns:featured:*")
    
    return CampaignResponse.from_orm(db_campaign)

# Social posts endpoints
@router.get("/social-posts/", response_model=List[SocialPostResponse])
async def get_social_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    platform: Optional[str] = None,
    post_type: Optional[str] = None,
    featured_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Get social posts with optional filtering"""
    
    cache_key = f"social_posts:list:{skip}:{limit}:{platform}:{post_type}:{featured_only}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return cached_data
    
    query = select(SocialPost)
    
    if platform:
        query = query.where(SocialPost.platform == platform)
    
    if post_type:
        query = query.where(SocialPost.post_type == post_type)
    
    if featured_only:
        query = query.where(SocialPost.is_featured == True)
    
    query = query.order_by(desc(SocialPost.posted_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    posts = result.scalars().all()
    
    post_responses = [SocialPostResponse.from_orm(post) for post in posts]
    
    # Cache for 10 minutes
    await redis_client.set(cache_key, post_responses, expire=600)
    
    return post_responses

@router.get("/social-posts/stats", response_model=dict)
async def get_social_media_stats(db: AsyncSession = Depends(get_db)):
    """Get social media statistics"""
    
    cached_data = await redis_client.get("social_posts:stats")
    if cached_data:
        return cached_data
    
    # Total posts
    total_posts_result = await db.execute(select(func.count(SocialPost.id)))
    total_posts = total_posts_result.scalar()
    
    # Total engagement
    total_likes_result = await db.execute(select(func.sum(SocialPost.likes_count)))
    total_likes = total_likes_result.scalar() or 0
    
    total_comments_result = await db.execute(select(func.sum(SocialPost.comments_count)))
    total_comments = total_comments_result.scalar() or 0
    
    total_shares_result = await db.execute(select(func.sum(SocialPost.shares_count)))
    total_shares = total_shares_result.scalar() or 0
    
    total_views_result = await db.execute(select(func.sum(SocialPost.views_count)))
    total_views = total_views_result.scalar() or 0
    
    # Platform breakdown
    platform_result = await db.execute(
        select(SocialPost.platform, func.count(SocialPost.id))
        .group_by(SocialPost.platform)
    )
    platform_breakdown = {platform: count for platform, count in platform_result.fetchall()}
    
    stats = {
        "total_posts": total_posts,
        "total_engagement": {
            "likes": total_likes,
            "comments": total_comments,
            "shares": total_shares,
            "views": total_views,
            "total": total_likes + total_comments + total_shares
        },
        "platform_breakdown": platform_breakdown,
        "avg_engagement_per_post": round((total_likes + total_comments + total_shares) / total_posts, 1) if total_posts > 0 else 0,
        "estimated_reach": total_views,
        "growth_metrics": {
            "followers_gained": 125000,
            "monthly_reach": 45000000,
            "engagement_rate": 8.5
        }
    }
    
    # Cache for 30 minutes
    await redis_client.set("social_posts:stats", stats, expire=1800)
    
    return stats

@router.post("/social-posts/", response_model=SocialPostResponse)
async def create_social_post(post_data: SocialPostCreate, db: AsyncSession = Depends(get_db)):
    """Create new social post"""
    
    db_post = SocialPost(**post_data.dict())
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    
    # Clear related caches
    await redis_client.delete("social_posts:stats")
    
    return SocialPostResponse.from_orm(db_post)