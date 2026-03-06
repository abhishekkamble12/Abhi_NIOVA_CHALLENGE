from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class ActionType(str, enum.Enum):
    VIEW = "view"
    CLICK = "click"
    LIKE = "like"
    SHARE = "share"
    SAVE = "save"
    DISMISS = "dismiss"


class UserBehavior(Base):
    """User behavior tracking for AI recommendations"""
    __tablename__ = "user_behaviors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), index=True)
    
    action_type = Column(SQLEnum(ActionType), nullable=False)
    
    # Engagement metrics
    time_spent = Column(Integer, default=0)  # seconds
    scroll_depth = Column(Float, default=0.0)  # percentage
    
    # Context
    device = Column(String(50))
    platform = Column(String(50))
    referrer = Column(String(500))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="behaviors")
    article = relationship("Article", back_populates="behaviors")
