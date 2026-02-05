from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.models.article import Article
from app.models.article_tag import ArticleTag
from app.models.user_behavior import UserBehavior
from app.models.user_preferences import UserPreferences
from app.schemas.news_feed import (
    ArticleCreate, ArticleResponse, FeedItemResponse, UserBehaviorCreate,
    RealNewsItemResponse, UserPreferencesCreate, UserPreferencesUpdate,
    UserPreferencesResponse, NewsSummaryRequest, NewsSummaryResponse
)
from app.services.nlp_service import NLPService
from app.services.news_service import NewsService
from datetime import datetime
from typing import List, Optional

router = APIRouter()
news_service = NewsService()

# ==================== REAL NEWS ENDPOINTS ====================

@router.get("/search", response_model=List[RealNewsItemResponse])
async def search_news(
    keyword: str = Query(..., min_length=1, description="Search keyword or topic"),
    sort_by: str = Query("publishedAt", description="Sort by: publishedAt, relevancy, popularity"),
    limit: int = Query(20, le=100),
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Search for real-time news based on user keywords.
    Results are personalized based on user preferences if user_id is provided.
    """
    
    # Fetch real news from NewsAPI
    articles = await news_service.fetch_news_by_keyword(
        keyword=keyword,
        sort_by=sort_by,
        page_size=limit
    )
    
    # If user provided, get their preferences and calculate relevance
    user_interests = []
    if user_id:
        prefs = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
        if prefs:
            user_interests = prefs.keywords or []
    
    # Process articles
    result_articles = []
    for article in articles:
        # Categorize article
        category = news_service.categorize_article(article["title"], article["description"])
        
        # Calculate relevance score
        relevance_score = news_service.calculate_relevance_score(
            user_interests,
            article["title"],
            article["description"]
        )
        
        # Generate summary if content available
        summary = None
        if article.get("content"):
            summary = news_service.summarize_article(article["content"])
        
        result_articles.append(RealNewsItemResponse(
            id=article["id"],
            title=article["title"],
            description=article["description"],
            content=article["content"],
            url=article["url"],
            source=article["source"],
            image_url=article.get("image_url"),
            published_at=article.get("published_at"),
            author=article.get("author"),
            keyword=keyword,
            category=category,
            trending=False,
            summary=summary,
            relevance_score=relevance_score
        ))
    
    # Sort by relevance if user_id provided
    if user_id and user_interests:
        result_articles.sort(key=lambda x: x.relevance_score, reverse=True)
    
    return result_articles

@router.get("/trending", response_model=List[RealNewsItemResponse])
async def get_trending_news(
    country: str = Query("us", description="Country code: us, gb, in, etc."),
    limit: int = Query(20, le=100),
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Fetch trending news headlines for a specific country.
    Optionally personalize based on user preferences.
    """
    
    # Fetch trending news
    articles = await news_service.fetch_trending_news(
        country=country,
        page_size=limit
    )
    
    # Get user preferences if user_id provided
    user_interests = []
    if user_id:
        prefs = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
        if prefs:
            user_interests = prefs.keywords or []
    
    # Process articles
    result_articles = []
    for article in articles:
        # Calculate relevance score based on user interests
        relevance_score = news_service.calculate_relevance_score(
            user_interests,
            article["title"],
            article["description"]
        )
        
        # Generate summary
        summary = None
        if article.get("content"):
            summary = news_service.summarize_article(article["content"])
        
        result_articles.append(RealNewsItemResponse(
            id=article["id"],
            title=article["title"],
            description=article["description"],
            content=article["content"],
            url=article["url"],
            source=article["source"],
            image_url=article.get("image_url"),
            published_at=article.get("published_at"),
            author=article.get("author"),
            category=article.get("category", "General"),
            trending=True,
            summary=summary,
            relevance_score=relevance_score
        ))
    
    # Sort by relevance if user_id provided
    if user_id and user_interests:
        result_articles.sort(key=lambda x: x.relevance_score, reverse=True)
    
    return result_articles

# ==================== ARTICLE SUMMARIZATION ====================

@router.post("/summarize", response_model=NewsSummaryResponse)
async def summarize_article(request: NewsSummaryRequest):
    """
    Generate AI-powered summary of article content.
    Perfect for reading summaries of long articles on the platform.
    """
    
    if not request.article_content:
        raise HTTPException(status_code=400, detail="Article content is required")
    
    # Generate summary
    summary = news_service.summarize_article(request.article_content)
    
    original_length = len(request.article_content.split())
    summary_length = len(summary.split())
    compression_ratio = 1 - (summary_length / original_length) if original_length > 0 else 0
    
    return NewsSummaryResponse(
        original_content=request.article_content[:500],
        summary=summary,
        summary_length=summary_length,
        original_length=original_length,
        compression_ratio=round(compression_ratio, 3)
    )

# ==================== USER PREFERENCES ====================

@router.post("/preferences/{user_id}", response_model=UserPreferencesResponse)
async def create_or_update_preferences(
    user_id: int,
    preferences: UserPreferencesCreate,
    db: Session = Depends(get_db)
):
    """
    Create or update user news preferences.
    This personalizes the news feed based on interests and categories.
    """
    
    # Check if user exists
    from app.models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if preferences exist
    existing_prefs = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
    
    if existing_prefs:
        # Update
        existing_prefs.keywords = preferences.keywords
        existing_prefs.categories = preferences.categories
        existing_prefs.preferred_sources = preferences.preferred_sources
        existing_prefs.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_prefs)
        return existing_prefs
    else:
        # Create
        db_prefs = UserPreferences(
            user_id=user_id,
            keywords=preferences.keywords,
            categories=preferences.categories,
            preferred_sources=preferences.preferred_sources
        )
        db.add(db_prefs)
        db.commit()
        db.refresh(db_prefs)
        return db_prefs

@router.get("/preferences/{user_id}", response_model=UserPreferencesResponse)
async def get_preferences(user_id: int, db: Session = Depends(get_db)):
    """Get user news preferences."""
    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
    if not prefs:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return prefs

@router.put("/preferences/{user_id}", response_model=UserPreferencesResponse)
async def update_preferences(
    user_id: int,
    preferences: UserPreferencesUpdate,
    db: Session = Depends(get_db)
):
    """Update user news preferences."""
    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
    if not prefs:
        raise HTTPException(status_code=404, detail="Preferences not found")
    
    if preferences.keywords is not None:
        prefs.keywords = preferences.keywords
    if preferences.categories is not None:
        prefs.categories = preferences.categories
    if preferences.preferred_sources is not None:
        prefs.preferred_sources = preferences.preferred_sources
    
    prefs.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(prefs)
    return prefs

@router.get("/personalized/{user_id}", response_model=List[RealNewsItemResponse])
async def get_personalized_feed(
    user_id: int,
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    """
    Get personalized news feed based on user preferences.
    Combines trending news with search results for user interests.
    """
    
    # Get user preferences
    prefs = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
    if not prefs or not prefs.keywords:
        # Return trending news if no preferences
        articles = await news_service.fetch_trending_news(page_size=limit)
    else:
        # Combine results from multiple keyword searches
        all_articles = []
        for keyword in prefs.keywords[:3]:  # Limit to top 3 keywords
            articles = await news_service.fetch_news_by_keyword(
                keyword=keyword,
                page_size=max(5, limit // 3)
            )
            all_articles.extend(articles)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article["url"] not in seen_urls:
                unique_articles.append(article)
                seen_urls.add(article["url"])
        
        articles = unique_articles[:limit]
    
    # Calculate relevance scores
    result_articles = []
    user_interests = prefs.keywords if prefs else []
    
    for article in articles:
        category = news_service.categorize_article(article["title"], article["description"])
        relevance_score = news_service.calculate_relevance_score(
            user_interests,
            article["title"],
            article["description"]
        )
        
        summary = None
        if article.get("content"):
            summary = news_service.summarize_article(article["content"])
        
        result_articles.append(RealNewsItemResponse(
            id=article["id"],
            title=article["title"],
            description=article["description"],
            content=article["content"],
            url=article["url"],
            source=article["source"],
            image_url=article.get("image_url"),
            published_at=article.get("published_at"),
            author=article.get("author"),
            category=category,
            trending=article.get("trending", False),
            summary=summary,
            relevance_score=relevance_score
        ))
    
    # Sort by relevance
    result_articles.sort(key=lambda x: x.relevance_score, reverse=True)
    
    return result_articles

# ==================== BEHAVIOR TRACKING ====================

@router.post("/track/behavior")
async def track_user_behavior(behavior: UserBehaviorCreate, db: Session = Depends(get_db)):
    """
    Track user interaction with articles.
    Actions: click, read, like, share
    This data helps personalize future recommendations.
    """
    
    article = db.query(Article).filter(Article.id == behavior.article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Save behavior
    db_behavior = UserBehavior(
        user_id=1,  # In production, get from auth
        article_id=behavior.article_id,
        action=behavior.action,
        read_time=behavior.read_time,
        scroll_depth=behavior.scroll_depth,
        timestamp=datetime.utcnow()
    )
    
    db.add(db_behavior)
    db.commit()
    db.refresh(db_behavior)
    
    return {
        "message": "Behavior tracked",
        "behavior_id": db_behavior.id,
        "action": behavior.action
    }

# ==================== CATEGORY BROWSING ====================

@router.get("/category/{category}", response_model=List[RealNewsItemResponse])
async def browse_by_category(
    category: str,
    limit: int = Query(20, le=100),
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Browse news by category.
    """
    
    # Map category to search keywords
    category_keywords = {
        "sports": "motorsport racing formula1",
        "technology": "artificial intelligence technology innovation",
        "business": "business finance economy market",
        "health": "health medical science",
        "entertainment": "entertainment movie celebrity",
        "science": "science research discovery",
        "politics": "politics election government",
    }
    
    keyword = category_keywords.get(category.lower(), category)
    
    # Fetch news
    articles = await news_service.fetch_news_by_keyword(keyword=keyword, page_size=limit)
    
    # Get user preferences for relevance scoring
    user_interests = []
    if user_id:
        prefs = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
        if prefs:
            user_interests = prefs.keywords or []
    
    # Process articles
    result_articles = []
    for article in articles:
        relevance_score = news_service.calculate_relevance_score(
            user_interests,
            article["title"],
            article["description"]
        )
        
        summary = None
        if article.get("content"):
            summary = news_service.summarize_article(article["content"])
        
        result_articles.append(RealNewsItemResponse(
            id=article["id"],
            title=article["title"],
            description=article["description"],
            content=article["content"],
            url=article["url"],
            source=article["source"],
            image_url=article.get("image_url"),
            published_at=article.get("published_at"),
            author=article.get("author"),
            category=category.capitalize(),
            trending=False,
            summary=summary,
            relevance_score=relevance_score
        ))
    
    return result_articles
