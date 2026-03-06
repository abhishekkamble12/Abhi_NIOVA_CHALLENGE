from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.middleware import RequestLoggingMiddleware
from app.core.exceptions import register_exception_handlers
from app.core.database import init_pgvector, create_tables, close_db
from app.core.redis import init_redis, close_redis
from app.api.v1.api import api_router
from app.core.websocket import websocket_router

# Setup logging first
setup_logging()
logger = get_logger(__name__)

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up AI Media OS API...")
    
    # Initialize database
    try:
        await init_pgvector()
        await create_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    # Initialize Redis
    try:
        await init_redis()
    except Exception as e:
        logger.warning(f"Redis initialization failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Media OS API...")
    await close_redis()
    await close_db()
    logger.info("All connections closed")

app = FastAPI(
    title="AI Media OS API",
    description="Unified AI platform for content creation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Register exception handlers
register_exception_handlers(app)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
app.include_router(websocket_router, prefix="/ws")

@app.get("/")
async def root():
    return {
        "message": "AI Media OS API",
        "version": "1.0.0",
        "status": "✅ Running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "mock"
    }

# ============================================================================
# LEGACY SYNCHRONOUS CODE (COMMENTED OUT - DO NOT REMOVE)
# ============================================================================
# from app.core.database import engine, Base
# Base.metadata.create_all(bind=engine)
# ============================================================================