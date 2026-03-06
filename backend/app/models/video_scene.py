from sqlalchemy import Column, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid

from app.core.database import Base
from app.core.config import settings


class VideoScene(Base):
    """Video scene segments with AI analysis"""
    __tablename__ = "video_scenes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    
    start_time = Column(Float, nullable=False)  # Start time in seconds
    end_time = Column(Float, nullable=False)    # End time in seconds
    
    # Scene analysis
    description = Column(Text)
    scene_type = Column(String(100))  # action, dialogue, transition, etc.
    objects_detected = Column(Text)   # JSON string of detected objects
    
    # AI suggestions
    suggested_cut = Column(String(50))  # keep, remove, trim
    confidence_score = Column(Float, default=0.0)
    
    # Vector embedding for scene similarity
    embedding = Column(Vector(settings.VECTOR_DIMENSION))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    video = relationship("Video", back_populates="scenes")
