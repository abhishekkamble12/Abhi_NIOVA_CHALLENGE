from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class ArticleBase(BaseModel):
    """Base Article schema"""
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    summary: Optional[str] = None
    url: str = Field(..., max_length=1000)
    source: Optional[str] = Field(None, max_length=100)
    author: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[list[str]] = None


class ArticleCreate(ArticleBase):
    """Schema for creating an article"""
    pass


class ArticleUpdate(BaseModel):
    """Schema for updating an article"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    summary: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[list[str]] = None


class ArticleResponse(ArticleBase):
    """Schema for article response"""
    id: UUID
    views: int
    clicks: int
    relevance_score: float
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class ArticleSearchResponse(BaseModel):
    """Schema for article search response"""
    article: ArticleResponse
    similarity: float


class ArticleListResponse(BaseModel):
    """Schema for article list response"""
    articles: list[ArticleResponse]
    total: int
    page: int
    page_size: int
