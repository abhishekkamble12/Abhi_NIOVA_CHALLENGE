"""FastAPI Backend - Connects AWS Services to Frontend"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os

# Add backend-aws to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend-aws'))

from services.aurora_service import get_db_connection
from services.cache_service import get_cache_service
from services.s3_service import get_s3_service
from services.bedrock_service import get_bedrock_service
from services.event_service import get_event_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting HiveMind API...")
    yield
    # Shutdown
    print("👋 Shutting down HiveMind API...")

app = FastAPI(
    title="HiveMind API",
    description="AI Media OS - AWS Backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "HiveMind API",
        "version": "1.0.0",
        "status": "✅ Running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health = {"status": "healthy", "services": {}}
    
    # Test Aurora
    try:
        async with get_db_connection() as conn:
            await conn.fetchval('SELECT 1')
        health["services"]["aurora"] = "✅ connected"
    except:
        health["services"]["aurora"] = "❌ disconnected"
    
    # Test Redis
    try:
        cache = get_cache_service()
        await cache.ping()
        health["services"]["redis"] = "✅ connected"
    except:
        health["services"]["redis"] = "❌ disconnected"
    
    return health

# Import routers
from api.social import router as social_router
from api.feed import router as feed_router
from api.videos import router as videos_router

app.include_router(social_router, prefix="/api/v1/social", tags=["social"])
app.include_router(feed_router, prefix="/api/v1/feed", tags=["feed"])
app.include_router(videos_router, prefix="/api/v1/videos", tags=["videos"])
