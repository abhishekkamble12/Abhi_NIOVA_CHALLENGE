"""News Feed API Endpoints"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.aurora_service import get_db_connection
from services.bedrock_service import get_bedrock_service
from services.cache_service import get_cache_service
import httpx

router = APIRouter()

NEWS_API_KEY = "your_newsapi_key"  # Set in .env

class ArticleIngest(BaseModel):
    title: str
    content: str
    url: str
    source: str
    category: str

@router.post("/articles/ingest")
async def ingest_article(article: ArticleIngest):
    """Ingest a new article"""
    # Generate embedding
    bedrock = get_bedrock_service()
    text = f"{article.title} {article.content}"
    embedding = await bedrock.generate_embedding(text)
    
    # Store in database
    async with get_db_connection() as conn:
        article_id = await conn.fetchval(
            """INSERT INTO articles (title, content, url, source, category, embedding) 
            VALUES ($1, $2, $3, $4, $5, $6) RETURNING id""",
            article.title, article.content, article.url, article.source, article.category, embedding
        )
    
    # Cache
    cache = get_cache_service()
    await cache.set_embedding(text, embedding)
    
    return {"id": article_id, **article.dict()}

@router.get("/articles/{article_id}")
async def get_article(article_id: int):
    """Get article by ID"""
    async with get_db_connection() as conn:
        article = await conn.fetchrow("SELECT * FROM articles WHERE id = $1", article_id)
    if not article:
        raise HTTPException(404, "Article not found")
    return dict(article)

@router.get("/feed/{user_id}")
async def get_personalized_feed(user_id: int, limit: int = 20):
    """Get personalized feed"""
    # Check cache
    cache = get_cache_service()
    cached = await cache.get_feed(user_id)
    if cached:
        return cached
    
    # Get from database
    async with get_db_connection() as conn:
        articles = await conn.fetch(
            "SELECT * FROM articles ORDER BY created_at DESC LIMIT $1",
            limit
        )
    
    result = [dict(a) for a in articles]
    await cache.set_feed(user_id, result)
    return result

@router.get("/real/search")
async def search_news(keyword: str, sort_by: str = "publishedAt", limit: int = 20, user_id: Optional[int] = None):
    """Search news via NewsAPI"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": keyword,
                "sortBy": sort_by,
                "pageSize": limit,
                "apiKey": NEWS_API_KEY
            }
        )
        data = response.json()
    return data.get("articles", [])

@router.get("/real/trending")
async def get_trending_news(country: str = "us", limit: int = 20, user_id: Optional[int] = None):
    """Get trending news"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://newsapi.org/v2/top-headlines",
            params={
                "country": country,
                "pageSize": limit,
                "apiKey": NEWS_API_KEY
            }
        )
        data = response.json()
    return data.get("articles", [])

@router.get("/real/personalized/{user_id}")
async def get_personalized_real_feed(user_id: int, limit: int = 20):
    """Get personalized real news feed"""
    # Get user preferences
    async with get_db_connection() as conn:
        prefs = await conn.fetchrow(
            "SELECT * FROM user_preferences WHERE user_id = $1",
            user_id
        )
    
    if not prefs:
        # Default to trending
        return await get_trending_news(limit=limit)
    
    # Search based on preferences
    keywords = prefs.get('keywords', 'technology')
    return await search_news(keyword=keywords, limit=limit)

@router.get("/real/category/{category}")
async def get_news_by_category(category: str, limit: int = 20, user_id: Optional[int] = None):
    """Get news by category"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://newsapi.org/v2/top-headlines",
            params={
                "category": category,
                "pageSize": limit,
                "apiKey": NEWS_API_KEY
            }
        )
        data = response.json()
    return data.get("articles", [])

@router.post("/real/summarize")
async def summarize_article(article_url: str, article_title: str, article_content: str):
    """Summarize article with Bedrock"""
    bedrock = get_bedrock_service()
    prompt = f"Summarize this article in 3 bullet points:\n\nTitle: {article_title}\n\nContent: {article_content[:1000]}"
    summary = await bedrock.generate_text(prompt, max_tokens=200)
    return {"summary": summary}

@router.get("/real/preferences/{user_id}")
async def get_user_preferences(user_id: int):
    """Get user preferences"""
    async with get_db_connection() as conn:
        prefs = await conn.fetchrow(
            "SELECT * FROM user_preferences WHERE user_id = $1",
            user_id
        )
    if not prefs:
        raise HTTPException(404, "Preferences not found")
    return dict(prefs)

@router.post("/real/preferences/{user_id}")
async def create_user_preferences(user_id: int, keywords: str, categories: str):
    """Create user preferences"""
    async with get_db_connection() as conn:
        await conn.execute(
            """INSERT INTO user_preferences (user_id, keywords, categories) 
            VALUES ($1, $2, $3)""",
            user_id, keywords, categories
        )
    return {"status": "created"}

@router.put("/real/preferences/{user_id}")
async def update_user_preferences(user_id: int, keywords: str, categories: str):
    """Update user preferences"""
    async with get_db_connection() as conn:
        await conn.execute(
            """UPDATE user_preferences SET keywords = $2, categories = $3 
            WHERE user_id = $1""",
            user_id, keywords, categories
        )
    return {"status": "updated"}
