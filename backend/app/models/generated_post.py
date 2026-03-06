from sqlalchemy import Column, String, DateTime, Text, Integer, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid
import enum

from app.core.database import Base
from app.core.config import settings


class PlatformType(str, enum.Enum):
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    FACEBOOK = "facebook"


class PostStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class GeneratedPost(Base):
    """AI-generated social media posts"""
    __tablename__ = "generated_posts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("brands.id", ondelete="CASCADE"), index=True)
    
    platform = Column(SQLEnum(PlatformType), nullable=False)
    status = Column(SQLEnum(PostStatus), default=PostStatus.DRAFT)
    
    content = Column(Text, nullable=False)
    hashtags = Column(Text)
    
    # Performance metrics
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    
    # AI metadata
    ai_model = Column(String(100))
    prompt_used = Column(Text)
    
    # Vector embedding for semantic search
    embedding = Column(Vector(settings.VECTOR_DIMENSION))
    
    scheduled_at = Column(DateTime(timezone=True))
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="generated_posts")
    brand = relationship("Brand", back_populates="generated_posts")
