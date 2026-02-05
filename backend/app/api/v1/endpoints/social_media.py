from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.brand import Brand
from app.models.generated_post import GeneratedPost
from app.models.engagement_metric import EngagementMetric
from app.schemas.brand import BrandCreate, BrandResponse, GeneratedPostCreate, GeneratedPostResponse, EngagementMetricResponse
from app.services.content_generation import ContentGenerationService
from datetime import datetime
from typing import List

router = APIRouter()

# ==================== BRAND ENDPOINTS ====================

@router.post("/brands", response_model=BrandResponse)
async def create_brand(brand: BrandCreate, db: Session = Depends(get_db)):
    """Create a new brand profile for content generation."""
    db_brand = Brand(
        user_id=1,  # Mock user_id
        name=brand.name,
        keywords=brand.keywords,
        tone=brand.tone,
        audience_persona=brand.audience_persona,
        platforms=brand.platforms,
        visual_identity=brand.visual_identity
    )
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand

@router.get("/brands/{brand_id}", response_model=BrandResponse)
async def get_brand(brand_id: int, db: Session = Depends(get_db)):
    """Get brand details."""
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand

@router.get("/brands", response_model=List[BrandResponse])
async def list_brands(db: Session = Depends(get_db)):
    """List all brands for the user."""
    brands = db.query(Brand).all()
    return brands

# ==================== CONTENT GENERATION ENDPOINTS ====================

@router.post("/generate/content", response_model=GeneratedPostResponse)
async def generate_content(
    brand_id: int,
    platform: str,
    db: Session = Depends(get_db)
):
    """
    Generate AI content for a brand.
    
    Process:
    1. Fetch brand data
    2. Use LLM to generate caption, hashtags, CTA
    3. Save to database
    4. Return generated post
    """
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    # Generate content using AI service
    caption = ContentGenerationService.generate_caption(brand.dict(), platform)
    hashtags = ContentGenerationService.generate_hashtags(brand.dict(), platform)
    cta = ContentGenerationService.generate_cta(brand.dict(), platform)
    
    # Save generated post
    db_post = GeneratedPost(
        brand_id=brand_id,
        platform=platform,
        caption=caption,
        hashtags=hashtags,
        cta=cta,
        published=False
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    return db_post

@router.get("/posts/{post_id}", response_model=GeneratedPostResponse)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get generated post details."""
    post = db.query(GeneratedPost).filter(GeneratedPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.get("/brand/{brand_id}/posts", response_model=List[GeneratedPostResponse])
async def get_brand_posts(brand_id: int, db: Session = Depends(get_db)):
    """Get all generated posts for a brand."""
    posts = db.query(GeneratedPost).filter(GeneratedPost.brand_id == brand_id).all()
    return posts

@router.put("/posts/{post_id}/publish")
async def publish_post(post_id: int, db: Session = Depends(get_db)):
    """Publish a generated post to social platform (mock)."""
    post = db.query(GeneratedPost).filter(GeneratedPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Mock API publishing - in production, call Twitter, Instagram, LinkedIn APIs
    post.published = True
    post.published_at = datetime.utcnow()
    post.post_id = f"{post.platform}_{post_id}_{int(datetime.utcnow().timestamp())}"
    
    db.commit()
    db.refresh(post)
    
    return {
        "message": "Post published successfully",
        "post": GeneratedPostResponse.from_orm(post)
    }

# ==================== ENGAGEMENT & FEEDBACK LOOP ====================

@router.post("/track/engagement/{post_id}")
async def track_engagement(
    post_id: int,
    likes: int = 0,
    comments: int = 0,
    shares: int = 0,
    impressions: int = 0,
    ctr: float = 0.0,
    db: Session = Depends(get_db)
):
    """
    Track post engagement metrics.
    Feedback loop: These metrics train the AI for better future content.
    """
    post = db.query(GeneratedPost).filter(GeneratedPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Calculate sentiment based on engagement
    total_engagement = likes + comments + shares
    sentiment = "positive" if total_engagement > 50 else "neutral"
    
    # Save engagement metric
    metric = EngagementMetric(
        brand_id=post.brand_id,
        post_id=post_id,
        likes=likes,
        comments=comments,
        shares=shares,
        impressions=impressions,
        click_through_rate=ctr,
        sentiment=sentiment
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    
    return {
        "message": "Engagement tracked",
        "metric": EngagementMetricResponse.from_orm(metric)
    }

@router.get("/analytics/brand/{brand_id}")
async def get_brand_analytics(brand_id: int, db: Session = Depends(get_db)):
    """Get analytics for a brand's generated content."""
    metrics = db.query(EngagementMetric).filter(EngagementMetric.brand_id == brand_id).all()
    
    if not metrics:
        raise HTTPException(status_code=404, detail="No engagement data")
    
    total_likes = sum(m.likes for m in metrics)
    total_comments = sum(m.comments for m in metrics)
    total_shares = sum(m.shares for m in metrics)
    avg_ctr = sum(m.click_through_rate for m in metrics) / len(metrics)
    
    return {
        "brand_id": brand_id,
        "total_posts": len(db.query(GeneratedPost).filter(GeneratedPost.brand_id == brand_id).all()),
        "total_likes": total_likes,
        "total_comments": total_comments,
        "total_shares": total_shares,
        "average_ctr": round(avg_ctr, 3),
        "metrics_count": len(metrics)
    }

@router.post("/optimize/prompts/{brand_id}")
async def optimize_prompts(brand_id: int, db: Session = Depends(get_db)):
    """
    Analyze past engagement and refine prompts for next generation.
    This is the FEEDBACK LOOP: Learn → Improve → Generate Better Content
    """
    # Get all engagement metrics for this brand
    metrics = db.query(EngagementMetric).filter(EngagementMetric.brand_id == brand_id).all()
    
    if not metrics:
        raise HTTPException(status_code=404, detail="No metrics to analyze")
    
    # Convert to dict for analysis
    engagement_data = [
        {
            "likes": m.likes,
            "comments": m.comments,
            "shares": m.shares,
            "engagement_score": (m.likes + m.comments * 2 + m.shares * 3) / max(m.impressions, 1)
        }
        for m in metrics
    ]
    
    # Get recommendations
    recommendations = ContentGenerationService.refine_prompt(engagement_data)
    
    return {
        "brand_id": brand_id,
        "optimization_complete": True,
        "recommendations": recommendations,
        "message": "Prompts optimized based on engagement data. Next generation will be better!"
    }
