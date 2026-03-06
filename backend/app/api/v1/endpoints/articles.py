from fastapi import APIRouter, Depends, status, Query
from uuid import UUID
from typing import Optional

from app.services.article_service import ArticleService, get_article_service
from app.schemas.article import (
    ArticleCreate,
    ArticleUpdate,
    ArticleResponse,
    ArticleListResponse,
    ArticleSearchResponse
)

router = APIRouter(prefix="/articles", tags=["articles"])


@router.post(
    "",
    response_model=ArticleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new article"
)
async def create_article(
    article_data: ArticleCreate,
    article_service: ArticleService = Depends(get_article_service)
):
    """Create a new article with automatic embedding generation"""
    return await article_service.create_article(article_data)


@router.get(
    "/{article_id}",
    response_model=ArticleResponse,
    summary="Get article by ID"
)
async def get_article(
    article_id: UUID,
    article_service: ArticleService = Depends(get_article_service)
):
    """Get a specific article"""
    article = await article_service.get_article(article_id)
    
    # Increment view count
    await article_service.increment_views(article_id)
    
    return article


@router.get(
    "",
    response_model=ArticleListResponse,
    summary="List articles"
)
async def list_articles(
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    article_service: ArticleService = Depends(get_article_service)
):
    """List articles with optional category filter and pagination"""
    skip = (page - 1) * page_size
    articles, total = await article_service.list_articles(category, skip, page_size)
    
    return ArticleListResponse(
        articles=articles,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get(
    "/search/semantic",
    response_model=list[ArticleSearchResponse],
    summary="Semantic article search"
)
async def search_articles(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=100),
    min_similarity: float = Query(0.5, ge=0.0, le=1.0),
    article_service: ArticleService = Depends(get_article_service)
):
    """Search articles using semantic similarity"""
    results = await article_service.search_articles(query, limit, min_similarity)
    
    return [
        ArticleSearchResponse(article=article, similarity=similarity)
        for article, similarity in results
    ]


@router.put(
    "/{article_id}",
    response_model=ArticleResponse,
    summary="Update article"
)
async def update_article(
    article_id: UUID,
    article_data: ArticleUpdate,
    article_service: ArticleService = Depends(get_article_service)
):
    """Update an article"""
    return await article_service.update_article(article_id, article_data)


@router.delete(
    "/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete article"
)
async def delete_article(
    article_id: UUID,
    article_service: ArticleService = Depends(get_article_service)
):
    """Delete an article"""
    await article_service.delete_article(article_id)
