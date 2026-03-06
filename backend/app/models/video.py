from sqlalchemy import Column, String, DateTime, Text, Integer, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid
import enum

from app.core.database import Base
from app.core.config import settings


class VideoStatus(str, enum.Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class Video(Base):
    """Video content with AI analysis"""
    __tablename__ = "videos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    # File information
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer)
    duration = Column(Float)  # Duration in seconds
    
    # Video metadata
    resolution = Column(String(20))  # e.g., "1920x1080"
    fps = Column(Integer)
    codec = Column(String(50))
    
    status = Column(SQLEnum(VideoStatus), default=VideoStatus.UPLOADING)
    
    # AI analysis
    transcript = Column(Text)
    summary = Column(Text)
    
    # Vector embedding for video content
    embedding = Column(Vector(settings.VECTOR_DIMENSION))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    scenes = relationship("VideoScene", back_populates="video", cascade="all, delete-orphan")
    captions = relationship("Caption", back_populates="video", cascade="all, delete-orphan")
