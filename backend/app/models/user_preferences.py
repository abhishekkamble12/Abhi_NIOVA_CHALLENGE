from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid

from app.core.database import Base
from app.core.config import settings


class UserPreferences(Base):
    """User preferences for personalization and recommendations"""
    __tablename__ = "user_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Content preferences
    preferred_categories = Column(ARRAY(String))
    preferred_sources = Column(ARRAY(String))
    blocked_sources = Column(ARRAY(String))
    
    # Platform preferences
    preferred_platforms = Column(ARRAY(String))  # instagram, linkedin, twitter
    
    # AI preferences
    content_tone = Column(String(50))  # professional, casual, humorous
    content_length = Column(String(20))  # short, medium, long
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    
    # Feed settings
    feed_refresh_interval = Column(Integer, default=60)  # minutes
    
    # Vector embedding for preference-based recommendations
    embedding = Column(Vector(settings.VECTOR_DIMENSION))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="preferences")
