from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.redis import redis_client
from app.models.race import Race, RaceResult, LapTime
from app.schemas.race import (
    RaceCreate, RaceUpdate, RaceResponse,
    RaceResultCreate, RaceResultResponse,
    LapTimeCreate, LapTimeResponse
)

router = APIRouter()

@router.get("/", response_model=List[RaceResponse])
async def get_races(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    season: Optional[int] = None,
    completed_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Get races with optional filtering"""
    
    cache_key = f"races:list:{skip}:{limit}:{season}:{completed_only}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return cached_data
    
    query = select(Race)
    
    if season:
        query = query.where(Race.season == season)
    
    if completed_only:
        query = query.where(Race.is_completed == True)
    
    query = query.order_by(desc(Race.race_date)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    races = result.scalars().all()
    
    race_responses = [RaceResponse.from_orm(race) for race in races]
    
    # Cache for 10 minutes
    await redis_client.set(cache_key, race_responses, expire=600)
    
    return race_responses

@router.get("/current-season", response_model=List[RaceResponse])
async def get_current_season_races(db: AsyncSession = Depends(get_db)):
    """Get races for current season (2026)"""
    
    cached_data = await redis_client.get("races:current_season")
    if cached_data:
        return cached_data
    
    current_year = datetime.now().year
    result = await db.execute(
        select(Race)
        .where(Race.season == current_year)
        .order_by(Race.round_number)
    )
    races = result.scalars().all()
    
    race_responses = [RaceResponse.from_orm(race) for race in races]
    
    # Cache for 1 hour
    await redis_client.set("races:current_season", race_responses, expire=3600)
    
    return race_responses

@router.get("/recent-results", response_model=List[dict])
async def get_recent_race_results(limit: int = Query(5, ge=1, le=10), db: AsyncSession = Depends(get_db)):
    """Get recent race results with performance data"""
    
    cached_data = await redis_client.get(f"races:recent_results:{limit}")
    if cached_data:
        return cached_data
    
    # Get recent completed races
    result = await db.execute(
        select(Race)
        .where(Race.is_completed == True)
        .order_by(desc(Race.race_date))
        .limit(limit)
    )
    races = result.scalars().all()
    
    recent_results = []
    for race in races:
        # Get race result for main driver
        result_query = await db.execute(
            select(RaceResult)
            .where(RaceResult.race_id == race.id)
            .where(RaceResult.driver_name == "Demo Driver")  # Main driver
        )
        race_result = result_query.scalar_one_or_none()
        
        if race_result:
            recent_results.append({
                "race": RaceResponse.from_orm(race),
                "result": RaceResultResponse.from_orm(race_result),
                "performance_summary": {
                    "position_gained": (race_result.starting_position or 0) - race_result.position,
                    "points_scored": race_result.points,
                    "fastest_lap": race_result.fastest_lap,
                    "podium": race_result.podium_finish
                }
            })
    
    # Cache for 30 minutes
    await redis_client.set(f"races:recent_results:{limit}", recent_results, expire=1800)
    
    return recent_results

@router.get("/statistics", response_model=dict)
async def get_racing_statistics(db: AsyncSession = Depends(get_db)):
    """Get comprehensive racing statistics"""
    
    cached_data = await redis_client.get("races:statistics")
    if cached_data:
        return cached_data
    
    # Total races
    total_races_result = await db.execute(
        select(func.count(RaceResult.id))
        .where(RaceResult.driver_name == "Demo Driver")
    )
    total_races = total_races_result.scalar()
    
    # Wins
    wins_result = await db.execute(
        select(func.count(RaceResult.id))
        .where(RaceResult.driver_name == "Demo Driver")
        .where(RaceResult.position == 1)
    )
    wins = wins_result.scalar()
    
    # Podiums
    podiums_result = await db.execute(
        select(func.count(RaceResult.id))
        .where(RaceResult.driver_name == "Demo Driver")
        .where(RaceResult.position <= 3)
    )
    podiums = podiums_result.scalar()
    
    # Pole positions
    poles_result = await db.execute(
        select(func.count(RaceResult.id))
        .where(RaceResult.driver_name == "Demo Driver")
        .where(RaceResult.pole_position == True)
    )
    poles = poles_result.scalar()
    
    # Fastest laps
    fastest_laps_result = await db.execute(
        select(func.count(RaceResult.id))
        .where(RaceResult.driver_name == "Demo Driver")
        .where(RaceResult.fastest_lap == True)
    )
    fastest_laps = fastest_laps_result.scalar()
    
    # Total points
    points_result = await db.execute(
        select(func.sum(RaceResult.points))
        .where(RaceResult.driver_name == "Demo Driver")
    )
    total_points = points_result.scalar() or 0
    
    statistics = {
        "career_summary": {
            "total_races": total_races,
            "wins": wins,
            "podiums": podiums,
            "pole_positions": poles,
            "fastest_laps": fastest_laps,
            "total_points": total_points,
            "win_rate": round((wins / total_races * 100), 1) if total_races > 0 else 0,
            "podium_rate": round((podiums / total_races * 100), 1) if total_races > 0 else 0
        },
        "current_season": {
            "position": 1,
            "points": 342,
            "wins_this_season": 15,
            "podiums_this_season": 18,
            "races_completed": 20
        },
        "records": {
            "best_championship_position": 1,
            "consecutive_wins": 5,
            "consecutive_podiums": 8,
            "points_in_single_season": 342
        }
    }
    
    # Cache for 1 hour
    await redis_client.set("races:statistics", statistics, expire=3600)
    
    return statistics

@router.get("/{race_id}", response_model=RaceResponse)
async def get_race(race_id: int, db: AsyncSession = Depends(get_db)):
    """Get specific race by ID"""
    
    cache_key = f"race:{race_id}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return cached_data
    
    result = await db.execute(select(Race).where(Race.id == race_id))
    race = result.scalar_one_or_none()
    
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    
    race_response = RaceResponse.from_orm(race)
    
    # Cache for 30 minutes
    await redis_client.set(cache_key, race_response, expire=1800)
    
    return race_response

@router.get("/{race_id}/results", response_model=List[RaceResultResponse])
async def get_race_results(race_id: int, db: AsyncSession = Depends(get_db)):
    """Get results for a specific race"""
    
    cache_key = f"race:{race_id}:results"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return cached_data
    
    result = await db.execute(
        select(RaceResult)
        .where(RaceResult.race_id == race_id)
        .order_by(RaceResult.position)
    )
    results = result.scalars().all()
    
    result_responses = [RaceResultResponse.from_orm(result) for result in results]
    
    # Cache for 1 hour
    await redis_client.set(cache_key, result_responses, expire=3600)
    
    return result_responses

@router.post("/", response_model=RaceResponse)
async def create_race(race_data: RaceCreate, db: AsyncSession = Depends(get_db)):
    """Create a new race"""
    
    db_race = Race(**race_data.dict())
    db.add(db_race)
    await db.commit()
    await db.refresh(db_race)
    
    # Clear related caches
    await redis_client.delete("races:current_season")
    await redis_client.delete("races:statistics")
    
    return RaceResponse.from_orm(db_race)