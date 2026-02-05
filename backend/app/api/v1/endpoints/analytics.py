from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random

from app.core.database import get_db
from app.core.redis import redis_client
from app.models.analytics import Analytics, UserSession
from app.schemas.analytics import (
    AnalyticsEvent, AnalyticsEventResponse,
    UserSessionCreate, UserSessionResponse,
    AnalyticsSummary, RealTimeAnalytics
)

router = APIRouter()

@router.post("/events", response_model=AnalyticsEventResponse)
async def track_event(event_data: AnalyticsEvent, db: AsyncSession = Depends(get_db)):
    """Track an analytics event"""
    
    db_event = Analytics(**event_data.dict())
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    
    # Update real-time counters in Redis
    await redis_client.increment("analytics:events:today")
    await redis_client.increment(f"analytics:events:{event_data.event_type}:today")
    
    return AnalyticsEventResponse.from_orm(db_event)

@router.post("/sessions", response_model=UserSessionResponse)
async def create_session(session_data: UserSessionCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user session"""
    
    db_session = UserSession(**session_data.dict())
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    
    # Update session counters
    await redis_client.increment("analytics:sessions:today")
    await redis_client.add_to_set("analytics:active_sessions", session_data.session_id)
    
    return UserSessionResponse.from_orm(db_session)

@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics summary for specified period"""
    
    cache_key = f"analytics:summary:{days}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return cached_data
    
    since = datetime.now() - timedelta(days=days)
    
    # Total sessions
    total_sessions_result = await db.execute(
        select(func.count(UserSession.id))
        .where(UserSession.created_at >= since)
    )
    total_sessions = total_sessions_result.scalar()
    
    # Total page views
    total_page_views_result = await db.execute(
        select(func.count(Analytics.id))
        .where(Analytics.event_type == "page_view")
        .where(Analytics.event_timestamp >= since)
    )
    total_page_views = total_page_views_result.scalar()
    
    # Unique visitors
    unique_visitors_result = await db.execute(
        select(func.count(func.distinct(UserSession.user_id)))
        .where(UserSession.created_at >= since)
        .where(UserSession.user_id.isnot(None))
    )
    unique_visitors = unique_visitors_result.scalar()
    
    # Average session duration
    avg_duration_result = await db.execute(
        select(func.avg(UserSession.duration))
        .where(UserSession.created_at >= since)
        .where(UserSession.duration.isnot(None))
    )
    avg_session_duration = avg_duration_result.scalar() or 0
    
    # Bounce rate
    bounce_rate_result = await db.execute(
        select(func.avg(UserSession.bounce_rate))
        .where(UserSession.created_at >= since)
        .where(UserSession.bounce_rate.isnot(None))
    )
    bounce_rate = bounce_rate_result.scalar() or 0
    
    # Top pages
    top_pages_result = await db.execute(
        select(Analytics.page_url, func.count(Analytics.id).label('views'))
        .where(Analytics.event_type == "page_view")
        .where(Analytics.event_timestamp >= since)
        .where(Analytics.page_url.isnot(None))
        .group_by(Analytics.page_url)
        .order_by(desc('views'))
        .limit(10)
    )
    top_pages = [{"page": page, "views": views} for page, views in top_pages_result.fetchall()]
    
    # Top referrers
    top_referrers_result = await db.execute(
        select(UserSession.referrer, func.count(UserSession.id).label('sessions'))
        .where(UserSession.created_at >= since)
        .where(UserSession.referrer.isnot(None))
        .group_by(UserSession.referrer)
        .order_by(desc('sessions'))
        .limit(10)
    )
    top_referrers = [{"referrer": ref, "sessions": sessions} for ref, sessions in top_referrers_result.fetchall()]
    
    # Device breakdown
    device_result = await db.execute(
        select(UserSession.device_type, func.count(UserSession.id))
        .where(UserSession.created_at >= since)
        .where(UserSession.device_type.isnot(None))
        .group_by(UserSession.device_type)
    )
    device_breakdown = {device: count for device, count in device_result.fetchall()}
    
    # Browser breakdown
    browser_result = await db.execute(
        select(UserSession.browser, func.count(UserSession.id))
        .where(UserSession.created_at >= since)
        .where(UserSession.browser.isnot(None))
        .group_by(UserSession.browser)
        .limit(10)
    )
    browser_breakdown = {browser: count for browser, count in browser_result.fetchall()}
    
    # Country breakdown
    country_result = await db.execute(
        select(UserSession.country, func.count(UserSession.id))
        .where(UserSession.created_at >= since)
        .where(UserSession.country.isnot(None))
        .group_by(UserSession.country)
        .limit(10)
    )
    country_breakdown = {country: count for country, count in country_result.fetchall()}
    
    summary = AnalyticsSummary(
        total_sessions=total_sessions,
        total_page_views=total_page_views,
        unique_visitors=unique_visitors,
        bounce_rate=float(bounce_rate * 100) if bounce_rate else 0,
        avg_session_duration=float(avg_session_duration) if avg_session_duration else 0,
        top_pages=top_pages,
        top_referrers=top_referrers,
        device_breakdown=device_breakdown,
        browser_breakdown=browser_breakdown,
        country_breakdown=country_breakdown
    )
    
    # Cache for 15 minutes
    await redis_client.set(cache_key, summary, expire=900)
    
    return summary

@router.get("/real-time", response_model=RealTimeAnalytics)
async def get_real_time_analytics(db: AsyncSession = Depends(get_db)):
    """Get real-time analytics data"""
    
    # Get active users from Redis
    active_sessions = await redis_client.get_set_members("analytics:active_sessions")
    active_users = len(active_sessions) if active_sessions else 0
    
    # Add some randomness for demo
    active_users += random.randint(-50, 100)
    active_users = max(0, active_users)
    
    # Current page views (last 5 minutes)
    five_minutes_ago = datetime.now() - timedelta(minutes=5)
    current_page_views_result = await db.execute(
        select(func.count(Analytics.id))
        .where(Analytics.event_type == "page_view")
        .where(Analytics.event_timestamp >= five_minutes_ago)
    )
    current_page_views = current_page_views_result.scalar()
    
    # Top active pages (last 30 minutes)
    thirty_minutes_ago = datetime.now() - timedelta(minutes=30)
    top_active_pages_result = await db.execute(
        select(Analytics.page_url, func.count(Analytics.id).label('views'))
        .where(Analytics.event_type == "page_view")
        .where(Analytics.event_timestamp >= thirty_minutes_ago)
        .where(Analytics.page_url.isnot(None))
        .group_by(Analytics.page_url)
        .order_by(desc('views'))
        .limit(5)
    )
    top_active_pages = [{"page": page, "views": views} for page, views in top_active_pages_result.fetchall()]
    
    # Recent events (last 10 minutes)
    ten_minutes_ago = datetime.now() - timedelta(minutes=10)
    recent_events_result = await db.execute(
        select(Analytics.event_name, Analytics.event_type, Analytics.event_timestamp)
        .where(Analytics.event_timestamp >= ten_minutes_ago)
        .order_by(desc(Analytics.event_timestamp))
        .limit(10)
    )
    recent_events = [
        {
            "event": event_name,
            "type": event_type,
            "timestamp": timestamp
        }
        for event_name, event_type, timestamp in recent_events_result.fetchall()
    ]
    
    # Performance metrics (mock data for demo)
    performance_metrics = {
        "avg_page_load_time": 850 + random.randint(-100, 200),
        "bounce_rate": 25.8 + random.uniform(-5, 5),
        "conversion_rate": 3.2 + random.uniform(-0.5, 0.5),
        "error_rate": 0.1 + random.uniform(-0.05, 0.05)
    }
    
    real_time_data = RealTimeAnalytics(
        active_users=active_users,
        current_page_views=current_page_views,
        top_active_pages=top_active_pages,
        recent_events=recent_events,
        performance_metrics=performance_metrics,
        timestamp=datetime.now()
    )
    
    return real_time_data

@router.get("/events", response_model=List[AnalyticsEventResponse])
async def get_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    event_type: Optional[str] = None,
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics events with filtering"""
    
    since = datetime.now() - timedelta(hours=hours)
    
    query = select(Analytics).where(Analytics.event_timestamp >= since)
    
    if event_type:
        query = query.where(Analytics.event_type == event_type)
    
    query = query.order_by(desc(Analytics.event_timestamp)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    events = result.scalars().all()
    
    return [AnalyticsEventResponse.from_orm(event) for event in events]

@router.get("/sessions", response_model=List[UserSessionResponse])
async def get_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
):
    """Get user sessions with filtering"""
    
    since = datetime.now() - timedelta(hours=hours)
    
    result = await db.execute(
        select(UserSession)
        .where(UserSession.created_at >= since)
        .order_by(desc(UserSession.created_at))
        .offset(skip)
        .limit(limit)
    )
    sessions = result.scalars().all()
    
    return [UserSessionResponse.from_orm(session) for session in sessions]

@router.get("/funnel", response_model=Dict[str, Any])
async def get_conversion_funnel(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get conversion funnel analytics"""
    
    cache_key = f"analytics:funnel:{days}"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return cached_data
    
    since = datetime.now() - timedelta(days=days)
    
    # Landing page visits
    landing_visits_result = await db.execute(
        select(func.count(Analytics.id))
        .where(Analytics.event_type == "page_view")
        .where(Analytics.page_url == "/")
        .where(Analytics.event_timestamp >= since)
    )
    landing_visits = landing_visits_result.scalar()
    
    # Helmet page visits
    helmet_visits_result = await db.execute(
        select(func.count(Analytics.id))
        .where(Analytics.event_type == "page_view")
        .where(Analytics.page_url.like("%/helmets%"))
        .where(Analytics.event_timestamp >= since)
    )
    helmet_visits = helmet_visits_result.scalar()
    
    # Performance page visits
    performance_visits_result = await db.execute(
        select(func.count(Analytics.id))
        .where(Analytics.event_type == "page_view")
        .where(Analytics.page_url.like("%/performance%"))
        .where(Analytics.event_timestamp >= since)
    )
    performance_visits = performance_visits_result.scalar()
    
    # Newsletter signups (mock data)
    newsletter_signups = random.randint(50, 200)
    
    funnel_data = {
        "steps": [
            {
                "name": "Landing Page",
                "visitors": landing_visits,
                "conversion_rate": 100.0
            },
            {
                "name": "Helmets Section",
                "visitors": helmet_visits,
                "conversion_rate": round((helmet_visits / landing_visits * 100), 1) if landing_visits > 0 else 0
            },
            {
                "name": "Performance Section",
                "visitors": performance_visits,
                "conversion_rate": round((performance_visits / landing_visits * 100), 1) if landing_visits > 0 else 0
            },
            {
                "name": "Newsletter Signup",
                "visitors": newsletter_signups,
                "conversion_rate": round((newsletter_signups / landing_visits * 100), 1) if landing_visits > 0 else 0
            }
        ],
        "overall_conversion_rate": round((newsletter_signups / landing_visits * 100), 1) if landing_visits > 0 else 0,
        "drop_off_points": [
            {
                "step": "Landing to Helmets",
                "drop_off_rate": round(((landing_visits - helmet_visits) / landing_visits * 100), 1) if landing_visits > 0 else 0
            },
            {
                "step": "Helmets to Performance",
                "drop_off_rate": round(((helmet_visits - performance_visits) / helmet_visits * 100), 1) if helmet_visits > 0 else 0
            }
        ]
    }
    
    # Cache for 1 hour
    await redis_client.set(cache_key, funnel_data, expire=3600)
    
    return funnel_data