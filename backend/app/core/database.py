from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator
import logging

from app.core.config import settings

# Configure SQL logging for development
if settings.is_development():
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# Create async engine with connection pooling
if "sqlite" in settings.DATABASE_URL:
    # SQLite: Use NullPool and no pool settings
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.is_development(),
        poolclass=NullPool,
    )
else:
    # PostgreSQL: Use connection pooling
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.is_development(),
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Declarative base for models
Base = declarative_base()

# Dependency for FastAPI routes
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Initialize pgvector extension (call on startup)
async def init_pgvector():
    """Initialize pgvector extension for PostgreSQL"""
    if "postgresql" in settings.DATABASE_URL:
        async with engine.begin() as conn:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            logging.info("pgvector extension initialized")

# Create all tables (call on startup)
async def create_tables():
    """Create all database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.info("Database tables created")

# Shutdown database connections (call on shutdown)
async def close_db():
    """Close all database connections"""
    await engine.dispose()
    logging.info("Database connections closed")

# ============================================================================
# LEGACY SYNCHRONOUS CODE (COMMENTED OUT - DO NOT REMOVE)
# ============================================================================
# from sqlalchemy import create_engine
# from sqlalchemy.orm import declarative_base, sessionmaker
#
# DATABASE_URL = "sqlite:///./test.db"
#
# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()
#
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
# ============================================================================
