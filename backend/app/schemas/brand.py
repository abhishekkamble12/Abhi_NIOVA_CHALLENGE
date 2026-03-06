from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


# Base schema with common fields
class BrandBase(BaseModel):
    """Base Brand schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    industry: Optional[str] = Field(None, max_length=100)
    tone: Optional[str] = Field(None, max_length=50)
    target_audience: Optional[str] = None
    brand_voice: Optional[str] = None


# Schema for creating a brand
class BrandCreate(BrandBase):
    """Schema for creating a brand"""
    pass


# Schema for updating a brand
class BrandUpdate(BaseModel):
    """Schema for updating a brand"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    industry: Optional[str] = Field(None, max_length=100)
    tone: Optional[str] = Field(None, max_length=50)
    target_audience: Optional[str] = None
    brand_voice: Optional[str] = None


# Schema for brand response
class BrandResponse(BrandBase):
    """Schema for brand response"""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Schema for brand list response
class BrandListResponse(BaseModel):
    """Schema for brand list response"""
    brands: list[BrandResponse]
    total: int
    page: int
    page_size: int
