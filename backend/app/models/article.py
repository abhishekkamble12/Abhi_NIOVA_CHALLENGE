from sqlalchemy import Column, String, DateTime, Text, Integer, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid

from app.core.database import Base
from app.core.config import settings


class Article(Base):
    """News articles for personalized feed"""
    __tablename__ = "articles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    url = Column(String(1000), unique=True, nullable=False, index=True)
    
    source = Column(String(100))
    author = Column(String(255))
    category = Column(String(100), index=True)
    tags = Column(ARRAY(String))
    
    # Engagement metrics
    views = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    relevance_score = Column(Float, default=0.0)
    
    # Vector embedding for semantic search
    embedding = Column(Vector(settings.VECTOR_DIMENSION))
    
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    behaviors = relationship("UserBehavior", back_populates="article")
