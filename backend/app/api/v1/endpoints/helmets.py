from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional

from app.core.database import get_db
from app.core.redis import redis_client
from app.models.helmet import Helmet, HelmetDesign
from app.schemas.helmet import (
    HelmetCreate, HelmetUpdate, HelmetResponse,
    HelmetDesignCreate, HelmetDesignResponse
)

router = APIRouter()

@router.get("/", response_model=List[HelmetResponse])
async def get_helmets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    season: Optional[str] = None,
    featured_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Get all helmets with optional filtering"""
    
    # Build cache key
    cache_key = f"helmets:list:{skip}:{limit}:{season}:{featured_only}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return cached_data
    
    # Build query
    query = select(Helmet)
    
    if season:
        query = query.where(Helmet.season == season)
    
    if featured_only:
        query = query.where(Helmet.is_featured == True)
    
    query = query.order_by(Helmet.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    helmets = result.scalars().all()
    
    # Convert to response format
    helmet_responses = [HelmetResponse.from_orm(helmet) for helmet in helmets]
    
    # Cache for 5 minutes
    await redis_client.set(cache_key, helmet_responses, expire=300)
    
    return helmet_responses

@router.get("/featured", response_model=List[HelmetResponse])
async def get_featured_helmets(db: AsyncSession = Depends(get_db)):
    """Get featured helmets for homepage"""
    
    cached_data = await redis_client.get("helmets:featured")
    if cached_data:
        return cached_data
    
    result = await db.execute(
        select(Helmet)
        .where(Helmet.is_featured == True)
        .order_by(Helmet.created_at.desc())
        .limit(6)
    )
    helmets = result.scalars().all()
    
    helmet_responses = [HelmetResponse.from_orm(helmet) for helmet in helmets]
    
    # Cache for 10 minutes
    await redis_client.set("helmets:featured", helmet_responses, expire=600)
    
    return helmet_responses

@router.get("/seasons", response_model=List[str])
async def get_helmet_seasons(db: AsyncSession = Depends(get_db)):
    """Get all available helmet seasons"""
    
    cached_data = await redis_client.get("helmets:seasons")
    if cached_data:
        return cached_data
    
    result = await db.execute(
        select(Helmet.season)
        .distinct()
        .order_by(Helmet.season.desc())
    )
    seasons = [row[0] for row in result.fetchall()]
    
    # Cache for 1 hour
    await redis_client.set("helmets:seasons", seasons, expire=3600)
    
    return seasons

@router.get("/stats", response_model=dict)
async def get_helmet_stats(db: AsyncSession = Depends(get_db)):
    """Get helmet collection statistics"""
    
    cached_data = await redis_client.get("helmets:stats")
    if cached_data:
        return cached_data
    
    # Get total count
    total_result = await db.execute(select(func.count(Helmet.id)))
    total_helmets = total_result.scalar()
    
    # Get championship helmets count
    championship_result = await db.execute(
        select(func.count(Helmet.id)).where(Helmet.is_championship_helmet == True)
    )
    championship_helmets = championship_result.scalar()
    
    # Get total races used
    races_result = await db.execute(select(func.sum(Helmet.races_used)))
    total_races = races_result.scalar() or 0
    
    # Get total wins
    wins_result = await db.execute(select(func.sum(Helmet.wins_with_helmet)))
    total_wins = wins_result.scalar() or 0
    
    # Get average weight
    weight_result = await db.execute(
        select(func.avg(Helmet.weight)).where(Helmet.weight.isnot(None))
    )
    avg_weight = weight_result.scalar() or 0
    
    stats = {
        "total_helmets": total_helmets,
        "championship_helmets": championship_helmets,
        "total_races_used": total_races,
        "total_wins": total_wins,
        "average_weight": round(float(avg_weight), 2) if avg_weight else 0,
        "seasons_covered": len(await get_helmet_seasons(db))
    }
    
    # Cache for 30 minutes
    await redis_client.set("helmets:stats", stats, expire=1800)
    
    return stats

@router.get("/{helmet_id}", response_model=HelmetResponse)
async def get_helmet(helmet_id: int, db: AsyncSession = Depends(get_db)):
    """Get specific helmet by ID"""
    
    cache_key = f"helmet:{helmet_id}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return cached_data
    
    result = await db.execute(select(Helmet).where(Helmet.id == helmet_id))
    helmet = result.scalar_one_or_none()
    
    if not helmet:
        raise HTTPException(status_code=404, detail="Helmet not found")
    
    helmet_response = HelmetResponse.from_orm(helmet)
    
    # Cache for 15 minutes
    await redis_client.set(cache_key, helmet_response, expire=900)
    
    return helmet_response

@router.post("/", response_model=HelmetResponse)
async def create_helmet(helmet_data: HelmetCreate, db: AsyncSession = Depends(get_db)):
    """Create a new helmet"""
    
    db_helmet = Helmet(**helmet_data.dict())
    db.add(db_helmet)
    await db.commit()
    await db.refresh(db_helmet)
    
    # Clear related caches
    await redis_client.delete("helmets:featured")
    await redis_client.delete("helmets:stats")
    await redis_client.delete("helmets:seasons")
    
    return HelmetResponse.from_orm(db_helmet)

@router.put("/{helmet_id}", response_model=HelmetResponse)
async def update_helmet(
    helmet_id: int,
    helmet_data: HelmetUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update helmet information"""
    
    result = await db.execute(select(Helmet).where(Helmet.id == helmet_id))
    helmet = result.scalar_one_or_none()
    
    if not helmet:
        raise HTTPException(status_code=404, detail="Helmet not found")
    
    # Update fields
    update_data = helmet_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(helmet, field, value)
    
    await db.commit()
    await db.refresh(helmet)
    
    # Clear caches
    await redis_client.delete(f"helmet:{helmet_id}")
    await redis_client.delete("helmets:featured")
    await redis_client.delete("helmets:stats")
    
    return HelmetResponse.from_orm(helmet)

@router.delete("/{helmet_id}")
async def delete_helmet(helmet_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a helmet"""
    
    result = await db.execute(select(Helmet).where(Helmet.id == helmet_id))
    helmet = result.scalar_one_or_none()
    
    if not helmet:
        raise HTTPException(status_code=404, detail="Helmet not found")
    
    await db.delete(helmet)
    await db.commit()
    
    # Clear caches
    await redis_client.delete(f"helmet:{helmet_id}")
    await redis_client.delete("helmets:featured")
    await redis_client.delete("helmets:stats")
    
    return {"message": "Helmet deleted successfully"}

@router.get("/{helmet_id}/designs", response_model=List[HelmetDesignResponse])
async def get_helmet_designs(helmet_id: int, db: AsyncSession = Depends(get_db)):
    """Get all design elements for a helmet"""
    
    cache_key = f"helmet:{helmet_id}:designs"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return cached_data
    
    result = await db.execute(
        select(HelmetDesign)
        .where(HelmetDesign.helmet_id == helmet_id)
        .order_by(HelmetDesign.layer_order)
    )
    designs = result.scalars().all()
    
    design_responses = [HelmetDesignResponse.from_orm(design) for design in designs]
    
    # Cache for 10 minutes
    await redis_client.set(cache_key, design_responses, expire=600)
    
    return design_responses

@router.post("/{helmet_id}/designs", response_model=HelmetDesignResponse)
async def create_helmet_design(
    helmet_id: int,
    design_data: HelmetDesignCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a design element to a helmet"""
    
    # Verify helmet exists
    result = await db.execute(select(Helmet).where(Helmet.id == helmet_id))
    helmet = result.scalar_one_or_none()
    
    if not helmet:
        raise HTTPException(status_code=404, detail="Helmet not found")
    
    # Create design
    design_dict = design_data.dict()
    design_dict["helmet_id"] = helmet_id
    
    db_design = HelmetDesign(**design_dict)
    db.add(db_design)
    await db.commit()
    await db.refresh(db_design)
    
    # Clear cache
    await redis_client.delete(f"helmet:{helmet_id}:designs")
    
    return HelmetDesignResponse.from_orm(db_design)