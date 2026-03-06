from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from app.models import Brand
from app.schemas.brand import BrandCreate, BrandUpdate
from app.services.vector_service import generate_embedding
from app.core.exceptions import NotFoundException
from app.core.logging import get_logger

logger = get_logger(__name__)


class BrandService:
    """Service for brand business logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_brand(self, user_id: UUID, brand_data: BrandCreate) -> Brand:
        """Create a new brand with embedding"""
        
        # Generate embedding from brand description
        text_for_embedding = f"{brand_data.name} {brand_data.description or ''} {brand_data.brand_voice or ''}"
        embedding = generate_embedding(text_for_embedding)
        
        # Create brand
        brand = Brand(
            user_id=user_id,
            name=brand_data.name,
            description=brand_data.description,
            industry=brand_data.industry,
            tone=brand_data.tone,
            target_audience=brand_data.target_audience,
            brand_voice=brand_data.brand_voice,
            embedding=embedding
        )
        
        self.db.add(brand)
        await self.db.commit()
        await self.db.refresh(brand)
        
        logger.info(f"Brand created: {brand.id}", extra={"extra_fields": {"brand_id": str(brand.id), "user_id": str(user_id)}})
        
        return brand
    
    async def get_brand(self, brand_id: UUID, user_id: Optional[UUID] = None) -> Brand:
        """Get brand by ID"""
        
        query = select(Brand).filter(Brand.id == brand_id)
        
        if user_id:
            query = query.filter(Brand.user_id == user_id)
        
        result = await self.db.execute(query)
        brand = result.scalar_one_or_none()
        
        if not brand:
            raise NotFoundException(
                message=f"Brand {brand_id} not found",
                details={"brand_id": str(brand_id)}
            )
        
        return brand
    
    async def list_brands(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Brand], int]:
        """List brands for a user with pagination"""
        
        # Get total count
        count_query = select(func.count()).select_from(Brand).filter(Brand.user_id == user_id)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Get brands
        query = (
            select(Brand)
            .filter(Brand.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Brand.created_at.desc())
        )
        
        result = await self.db.execute(query)
        brands = result.scalars().all()
        
        return list(brands), total
    
    async def update_brand(
        self,
        brand_id: UUID,
        user_id: UUID,
        brand_data: BrandUpdate
    ) -> Brand:
        """Update brand"""
        
        brand = await self.get_brand(brand_id, user_id)
        
        # Update fields
        update_data = brand_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(brand, field, value)
        
        # Regenerate embedding if relevant fields changed
        if any(field in update_data for field in ['name', 'description', 'brand_voice']):
            text_for_embedding = f"{brand.name} {brand.description or ''} {brand.brand_voice or ''}"
            brand.embedding = generate_embedding(text_for_embedding)
        
        await self.db.commit()
        await self.db.refresh(brand)
        
        logger.info(f"Brand updated: {brand.id}", extra={"extra_fields": {"brand_id": str(brand.id)}})
        
        return brand
    
    async def delete_brand(self, brand_id: UUID, user_id: UUID) -> None:
        """Delete brand"""
        
        brand = await self.get_brand(brand_id, user_id)
        
        await self.db.delete(brand)
        await self.db.commit()
        
        logger.info(f"Brand deleted: {brand_id}", extra={"extra_fields": {"brand_id": str(brand_id)}})


# Dependency injection
def get_brand_service(db: AsyncSession) -> BrandService:
    """Get BrandService instance"""
    return BrandService(db)
