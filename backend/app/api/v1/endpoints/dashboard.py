from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from datetime import datetime, timedelta
import random

from app.core.database import get_db
from app.core.redis import redis_client

router = APIRouter()

@router.get("/overview")
async def get_dashboard_overview(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get dashboard overview with key metrics"""
    
    # Check cache first
    cached_data = await redis_client.get("dashboard:overview")
    if cached_data:
        return cached_data
    
    # Generate mock data (in real app, query from database)
    overview_data = {
        "racing_stats": {
            "current_position": 1,
            "championship_points": 342,
            "race_wins": 15,
            "podium_finishes": 42,
            "pole_positions": 8,
            "fastest_laps": 12
        },
        "performance_metrics": {
            "lighthouse_score": 100,
            "lcp": "0.8s",
            "fid": "12ms",
            "cls": "0.02",
            "uptime": 99.9
        },
        "social_impact": {
            "total_followers": 15200000,
            "monthly_reach": 45000000,
            "engagement_rate": 8.5,
            "content_views": 125000000
        },
        "recent_activity": [
            {
                "type": "race_result",
                "title": "Monaco GP Victory",
                "description": "P1 finish with fastest lap",
                "timestamp": datetime.now() - timedelta(days=2),
                "icon": "🏆"
            },
            {
                "type": "content",
                "title": "New Helmet Design Revealed",
                "description": "Chrome Edition for upcoming race",
                "timestamp": datetime.now() - timedelta(days=5),
                "icon": "🪖"
            },
            {
                "type": "campaign",
                "title": "Sustainability Campaign Launch",
                "description": "Green Future initiative goes live",
                "timestamp": datetime.now() - timedelta(days=7),
                "icon": "🌱"
            }
        ],
        "upcoming_events": [
            {
                "type": "race",
                "title": "Spanish Grand Prix",
                "date": datetime.now() + timedelta(days=14),
                "location": "Barcelona, Spain"
            },
            {
                "type": "campaign",
                "title": "Gaming Tournament",
                "date": datetime.now() + timedelta(days=21),
                "location": "Online"
            }
        ],
        "last_updated": datetime.now()
    }
    
    # Cache for 5 minutes
    await redis_client.set("dashboard:overview", overview_data, expire=300)
    
    return overview_data

@router.get("/live-stats")
async def get_live_stats() -> Dict[str, Any]:
    """Get real-time racing and performance statistics"""
    
    # Generate live data (in real app, this would come from telemetry)
    live_stats = {
        "racing": {
            "current_speed": 320 + random.randint(-30, 30),
            "lap_time": "1:23.456",
            "position": 1,
            "gap_to_next": "+0.234",
            "tire_temperature": 85 + random.randint(-10, 15),
            "fuel_remaining": 45.2,
            "drs_available": True,
            "sector_times": ["28.123", "31.456", "23.877"]
        },
        "website": {
            "active_users": 1250 + random.randint(-200, 300),
            "requests_per_minute": 850 + random.randint(-100, 200),
            "response_time": 45 + random.randint(-15, 25),
            "error_rate": 0.1 + random.uniform(-0.05, 0.05),
            "cache_hit_rate": 95.5 + random.uniform(-2, 2)
        },
        "social": {
            "mentions_per_hour": 450 + random.randint(-100, 150),
            "sentiment_score": 8.2 + random.uniform(-0.5, 0.5),
            "trending_hashtags": ["#RacingDemo", "#PerformanceFirst", "#ChampionMindset"]
        },
        "timestamp": datetime.now()
    }
    
    return live_stats

@router.get("/performance-summary")
async def get_performance_summary(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get comprehensive performance summary"""
    
    cached_data = await redis_client.get("dashboard:performance")
    if cached_data:
        return cached_data
    
    performance_data = {
        "web_vitals": {
            "lcp": 0.8,
            "fid": 12,
            "cls": 0.02,
            "fcp": 0.6,
            "ttfb": 150
        },
        "lighthouse": {
            "performance": 100,
            "accessibility": 100,
            "best_practices": 100,
            "seo": 100,
            "pwa": 95
        },
        "system_health": {
            "cpu_usage": 25.5,
            "memory_usage": 68.2,
            "disk_usage": 45.8,
            "network_latency": 12.3,
            "database_connections": 15,
            "cache_status": "healthy"
        },
        "uptime": {
            "current_uptime": 99.98,
            "monthly_uptime": 99.95,
            "yearly_uptime": 99.92,
            "last_incident": datetime.now() - timedelta(days=45)
        },
        "traffic": {
            "daily_visitors": 125000,
            "page_views": 450000,
            "bounce_rate": 25.8,
            "avg_session_duration": 185.5,
            "conversion_rate": 3.2
        },
        "last_updated": datetime.now()
    }
    
    # Cache for 2 minutes
    await redis_client.set("dashboard:performance", performance_data, expire=120)
    
    return performance_data

@router.get("/analytics-summary")
async def get_analytics_summary(
    days: int = 30,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get analytics summary for specified period"""
    
    cache_key = f"dashboard:analytics:{days}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return cached_data
    
    # Generate mock analytics data
    analytics_data = {
        "period": {
            "start_date": datetime.now() - timedelta(days=days),
            "end_date": datetime.now(),
            "days": days
        },
        "overview": {
            "total_sessions": 125000 * (days / 30),
            "unique_visitors": 85000 * (days / 30),
            "page_views": 450000 * (days / 30),
            "bounce_rate": 25.8,
            "avg_session_duration": 185.5
        },
        "top_pages": [
            {"page": "/", "views": 125000, "unique_views": 95000},
            {"page": "/helmets", "views": 85000, "unique_views": 65000},
            {"page": "/performance", "views": 65000, "unique_views": 45000},
            {"page": "/racing", "views": 55000, "unique_views": 40000}
        ],
        "traffic_sources": [
            {"source": "Direct", "sessions": 45000, "percentage": 36.0},
            {"source": "Social Media", "sessions": 35000, "percentage": 28.0},
            {"source": "Search", "sessions": 25000, "percentage": 20.0},
            {"source": "Referral", "sessions": 20000, "percentage": 16.0}
        ],
        "device_breakdown": {
            "mobile": 65.2,
            "desktop": 28.5,
            "tablet": 6.3
        },
        "geographic_data": [
            {"country": "United States", "sessions": 35000, "percentage": 28.0},
            {"country": "United Kingdom", "sessions": 25000, "percentage": 20.0},
            {"country": "Germany", "sessions": 15000, "percentage": 12.0},
            {"country": "France", "sessions": 12000, "percentage": 9.6},
            {"country": "Italy", "sessions": 10000, "percentage": 8.0}
        ],
        "last_updated": datetime.now()
    }
    
    # Cache for 10 minutes
    await redis_client.set(cache_key, analytics_data, expire=600)
    
    return analytics_data