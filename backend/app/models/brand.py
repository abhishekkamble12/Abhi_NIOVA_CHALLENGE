from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid

from app.core.database import Base
from app.core.config import settings


class Brand(Base):
    """Brand model for managing brand identity and voice"""
    __tablename__ = "brands"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    industry = Column(String(100))
    tone = Column(String(50))  # professional, casual, friendly, etc.
    target_audience = Column(Text)
    brand_voice = Column(Text)
    
    # Vector embedding for brand identity
    embedding = Column(Vector(settings.VECTOR_DIMENSION))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="brands")
    generated_posts = relationship("GeneratedPost", back_populates="brand", cascade="all, delete-orphan")
