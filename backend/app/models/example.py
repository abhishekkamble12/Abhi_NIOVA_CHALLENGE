"""
Example models demonstrating pgvector usage with SQLAlchemy 2.0 async

Usage in your models:
    from app.models.example import Article, SocialPost
    from app.core.database import get_db
    from sqlalchemy import select
    
    async def get_similar_articles(db: AsyncSession, embedding: list[float], limit: int = 5):
        result = await db.execute(
            select(Article)
            .order_by(Article.embedding.l2_distance(embedding))
            .limit(limit)
        )
        return result.scalars().all()
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.core.database import Base
from app.core.config import settings


class Article(Base):
    """News article with vector embeddings for semantic search"""
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    url = Column(String(1000), unique=True, nullable=False)
    source = Column(String(100))
    
    # Vector embedding for semantic search
    embedding = Column(Vector(settings.VECTOR_DIMENSION))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SocialPost(Base):
    """Social media post with performance metrics and embeddings"""
    __tablename__ = "social_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False)  # instagram, linkedin, twitter
    content = Column(Text, nullable=False)
    
    # Performance metrics
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    
    # Vector embedding for content similarity
    embedding = Column(Vector(settings.VECTOR_DIMENSION))
    
    posted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class VideoSegment(Base):
    """Video segment with scene embeddings"""
    __tablename__ = "video_segments"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    
    # Scene description and embedding
    description = Column(Text)
    embedding = Column(Vector(settings.VECTOR_DIMENSION))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ============================================================================
# VECTOR SEARCH HELPER FUNCTIONS
# ============================================================================

async def vector_search_articles(db, query_embedding: list[float], limit: int = 10):
    """Search articles by semantic similarity using L2 distance"""
    from sqlalchemy import select
    
    result = await db.execute(
        select(Article)
        .order_by(Article.embedding.l2_distance(query_embedding))
        .limit(limit)
    )
    return result.scalars().all()


async def vector_search_posts(db, query_embedding: list[float], platform: str = None, limit: int = 10):
    """Search social posts by semantic similarity"""
    from sqlalchemy import select
    
    query = select(SocialPost)
    if platform:
        query = query.filter(SocialPost.platform == platform)
    
    query = query.order_by(SocialPost.embedding.l2_distance(query_embedding)).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def find_similar_segments(db, segment_id: int, limit: int = 5):
    """Find similar video segments based on scene embeddings"""
    from sqlalchemy import select
    
    # Get the target segment
    result = await db.execute(
        select(VideoSegment).filter(VideoSegment.id == segment_id)
    )
    target = result.scalar_one_or_none()
    
    if not target or not target.embedding:
        return []
    
    # Find similar segments
    result = await db.execute(
        select(VideoSegment)
        .filter(VideoSegment.id != segment_id)
        .order_by(VideoSegment.embedding.l2_distance(target.embedding))
        .limit(limit)
    )
    return result.scalars().all()
