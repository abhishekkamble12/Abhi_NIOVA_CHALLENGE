from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.services.brand_service import BrandService, get_brand_service
from app.schemas.brand import (
    BrandCreate,
    BrandUpdate,
    BrandResponse,
    BrandListResponse
)

router = APIRouter(prefix="/brands", tags=["brands"])


@router.post(
    "",
    response_model=BrandResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new brand"
)
async def create_brand(
    brand_data: BrandCreate,
    user_id: UUID,  # TODO: Get from auth token
    brand_service: BrandService = Depends(get_brand_service)
):
    """Create a new brand with automatic embedding generation"""
    return await brand_service.create_brand(user_id, brand_data)


@router.get(
    "/{brand_id}",
    response_model=BrandResponse,
    summary="Get brand by ID"
)
async def get_brand(
    brand_id: UUID,
    user_id: UUID,  # TODO: Get from auth token
    brand_service: BrandService = Depends(get_brand_service)
):
    """Get a specific brand"""
    return await brand_service.get_brand(brand_id, user_id)


@router.get(
    "",
    response_model=BrandListResponse,
    summary="List user's brands"
)
async def list_brands(
    user_id: UUID,  # TODO: Get from auth token
    page: int = 1,
    page_size: int = 20,
    brand_service: BrandService = Depends(get_brand_service)
):
    """List all brands for a user with pagination"""
    skip = (page - 1) * page_size
    brands, total = await brand_service.list_brands(user_id, skip, page_size)
    
    return BrandListResponse(
        brands=brands,
        total=total,
        page=page,
        page_size=page_size
    )


@router.put(
    "/{brand_id}",
    response_model=BrandResponse,
    summary="Update brand"
)
async def update_brand(
    brand_id: UUID,
    brand_data: BrandUpdate,
    user_id: UUID,  # TODO: Get from auth token
    brand_service: BrandService = Depends(get_brand_service)
):
    """Update a brand"""
    return await brand_service.update_brand(brand_id, user_id, brand_data)


@router.delete(
    "/{brand_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete brand"
)
async def delete_brand(
    brand_id: UUID,
    user_id: UUID,  # TODO: Get from auth token
    brand_service: BrandService = Depends(get_brand_service)
):
    """Delete a brand"""
    await brand_service.delete_brand(brand_id, user_id)
