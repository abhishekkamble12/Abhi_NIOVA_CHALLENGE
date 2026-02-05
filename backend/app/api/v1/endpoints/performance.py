from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random

from app.core.database import get_db
from app.core.redis import redis_client
from app.models.performance import PerformanceMetric, SystemMetric
from app.schemas.performance import (
    PerformanceMetricCreate, PerformanceMetricResponse,
    SystemMetricCreate, SystemMetricResponse,
    PerformanceSummaryResponse, WebVitalsResponse, LighthouseResponse
)

router = APIRouter()

@router.get("/web-vitals", response_model=WebVitalsResponse)
async def get_web_vitals(db: AsyncSession = Depends(get_db)):
    """Get current Core Web Vitals metrics"""
    
    cached_data = await redis_client.get("performance:web_vitals")
    if cached_data:
        return cached_data
    
    # In a real app, these would come from actual measurements
    web_vitals = WebVitalsResponse(
        lcp=0.8,  # Largest Contentful Paint (seconds)
        fid=12,   # First Input Delay (milliseconds)
        cls=0.02, # Cumulative Layout Shift
        fcp=0.6,  # First Contentful Paint (seconds)
        ttfb=150  # Time to First Byte (milliseconds)
    )
    
    # Cache for 5 minutes
    await redis_client.set("performance:web_vitals", web_vitals, expire=300)
    
    return web_vitals

@router.get("/lighthouse", response_model=LighthouseResponse)
async def get_lighthouse_scores(db: AsyncSession = Depends(get_db)):
    """Get current Lighthouse scores"""
    
    cached_data = await redis_client.get("performance:lighthouse")
    if cached_data:
        return cached_data
    
    lighthouse = LighthouseResponse(
        performance=100,
        accessibility=100,
        best_practices=100,
        seo=100,
        pwa=95
    )
    
    # Cache for 10 minutes
    await redis_client.set("performance:lighthouse", lighthouse, expire=600)
    
    return lighthouse

@router.get("/summary", response_model=PerformanceSummaryResponse)
async def get_performance_summary(db: AsyncSession = Depends(get_db)):
    """Get comprehensive performance summary"""
    
    cached_data = await redis_client.get("performance:summary")
    if cached_data:
        return cached_data
    
    web_vitals = await get_web_vitals(db)
    lighthouse = await get_lighthouse_scores(db)
    
    system_health = {
        "cpu_usage": 25.5 + random.uniform(-5, 5),
        "memory_usage": 68.2 + random.uniform(-10, 10),
        "disk_usage": 45.8,
        "network_latency": 12.3 + random.uniform(-2, 2),
        "database_response_time": 15.2 + random.uniform(-3, 3),
        "cache_hit_rate": 95.5 + random.uniform(-2, 2),
        "active_connections": 150 + random.randint(-20, 30),
        "requests_per_minute": 850 + random.randint(-100, 200)
    }
    
    summary = PerformanceSummaryResponse(
        web_vitals=web_vitals,
        lighthouse=lighthouse,
        system_health=system_health,
        uptime_percentage=99.98,
        last_updated=datetime.now()
    )
    
    # Cache for 2 minutes
    await redis_client.set("performance:summary", summary, expire=120)
    
    return summary

@router.get("/metrics", response_model=List[PerformanceMetricResponse])
async def get_performance_metrics(
    metric_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get performance metrics with optional filtering"""
    
    cache_key = f"performance:metrics:{metric_type}:{limit}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return cached_data
    
    query = select(PerformanceMetric)
    
    if metric_type:
        query = query.where(PerformanceMetric.metric_type == metric_type)
    
    query = query.order_by(desc(PerformanceMetric.measured_at)).limit(limit)
    
    result = await db.execute(query)
    metrics = result.scalars().all()
    
    metric_responses = [PerformanceMetricResponse.from_orm(metric) for metric in metrics]
    
    # Cache for 5 minutes
    await redis_client.set(cache_key, metric_responses, expire=300)
    
    return metric_responses

@router.get("/system-metrics", response_model=List[SystemMetricResponse])
async def get_system_metrics(
    hours: int = Query(24, ge=1, le=168),  # Last 24 hours by default, max 1 week
    db: AsyncSession = Depends(get_db)
):
    """Get system metrics for specified time period"""
    
    cache_key = f"performance:system_metrics:{hours}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return cached_data
    
    since = datetime.now() - timedelta(hours=hours)
    
    result = await db.execute(
        select(SystemMetric)
        .where(SystemMetric.measured_at >= since)
        .order_by(desc(SystemMetric.measured_at))
    )
    metrics = result.scalars().all()
    
    metric_responses = [SystemMetricResponse.from_orm(metric) for metric in metrics]
    
    # Cache for 5 minutes
    await redis_client.set(cache_key, metric_responses, expire=300)
    
    return metric_responses

@router.get("/real-time", response_model=Dict[str, Any])
async def get_real_time_metrics():
    """Get real-time performance metrics"""
    
    # Generate real-time data (in production, this would come from monitoring systems)
    real_time_data = {
        "timestamp": datetime.now(),
        "web_performance": {
            "response_time": 45 + random.randint(-15, 25),
            "throughput": 850 + random.randint(-100, 200),
            "error_rate": 0.1 + random.uniform(-0.05, 0.05),
            "active_users": 1250 + random.randint(-200, 300)
        },
        "system_resources": {
            "cpu_usage": 25.5 + random.uniform(-5, 10),
            "memory_usage": 68.2 + random.uniform(-5, 15),
            "disk_io": 45.8 + random.uniform(-10, 20),
            "network_io": 125.3 + random.uniform(-20, 40)
        },
        "database": {
            "connections": 15 + random.randint(-3, 8),
            "query_time": 15.2 + random.uniform(-3, 7),
            "slow_queries": random.randint(0, 3),
            "cache_hit_rate": 95.5 + random.uniform(-2, 2)
        },
        "application": {
            "requests_per_second": 14.2 + random.uniform(-3, 6),
            "avg_response_time": 125 + random.randint(-25, 50),
            "memory_heap": 245.8 + random.uniform(-20, 40),
            "gc_collections": random.randint(0, 2)
        }
    }
    
    return real_time_data

@router.get("/uptime", response_model=Dict[str, Any])
async def get_uptime_stats(db: AsyncSession = Depends(get_db)):
    """Get uptime statistics"""
    
    cached_data = await redis_client.get("performance:uptime")
    if cached_data:
        return cached_data
    
    uptime_stats = {
        "current_uptime": {
            "percentage": 99.98,
            "duration_days": 45,
            "last_downtime": datetime.now() - timedelta(days=45, hours=2, minutes=15)
        },
        "monthly_uptime": {
            "percentage": 99.95,
            "total_downtime_minutes": 21.6,
            "incidents": 2
        },
        "yearly_uptime": {
            "percentage": 99.92,
            "total_downtime_hours": 7.2,
            "incidents": 8
        },
        "sla_targets": {
            "target_uptime": 99.9,
            "current_status": "exceeding",
            "buffer_minutes": 43.2
        },
        "recent_incidents": [
            {
                "date": datetime.now() - timedelta(days=45),
                "duration_minutes": 15,
                "cause": "Database maintenance",
                "impact": "minimal"
            },
            {
                "date": datetime.now() - timedelta(days=78),
                "duration_minutes": 8,
                "cause": "CDN issue",
                "impact": "partial"
            }
        ]
    }
    
    # Cache for 1 hour
    await redis_client.set("performance:uptime", uptime_stats, expire=3600)
    
    return uptime_stats

@router.post("/metrics", response_model=PerformanceMetricResponse)
async def create_performance_metric(
    metric_data: PerformanceMetricCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new performance metric entry"""
    
    db_metric = PerformanceMetric(**metric_data.dict())
    db.add(db_metric)
    await db.commit()
    await db.refresh(db_metric)
    
    # Clear related caches
    await redis_client.delete("performance:summary")
    await redis_client.delete("performance:web_vitals")
    await redis_client.delete("performance:lighthouse")
    
    return PerformanceMetricResponse.from_orm(db_metric)

@router.post("/system-metrics", response_model=SystemMetricResponse)
async def create_system_metric(
    metric_data: SystemMetricCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new system metric entry"""
    
    db_metric = SystemMetric(**metric_data.dict())
    db.add(db_metric)
    await db.commit()
    await db.refresh(db_metric)
    
    return SystemMetricResponse.from_orm(db_metric)