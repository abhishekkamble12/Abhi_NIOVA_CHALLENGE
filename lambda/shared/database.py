"""
Database connection utilities for Lambda functions
"""
import os
import json
import boto3
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from contextlib import asynccontextmanager

# Global engine (reused across invocations)
_engine = None
_session_factory = None


def get_db_credentials():
    """
    Get database credentials from Secrets Manager
    """
    secret_name = os.environ.get('DB_SECRET_NAME', 'hivemind/aurora/credentials')
    region = os.environ.get('AWS_REGION', 'us-east-1')
    
    client = boto3.client('secretsmanager', region_name=region)
    response = client.get_secret_value(SecretId=secret_name)
    
    return json.loads(response['SecretString'])


def get_database_url():
    """
    Build database URL from environment or Secrets Manager
    """
    # Try environment variable first (for local testing)
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        return db_url
    
    # Get from Secrets Manager
    creds = get_db_credentials()
    
    return (
        f"postgresql+asyncpg://{creds['username']}:{creds['password']}"
        f"@{creds['host']}:{creds['port']}/{creds['database']}"
    )


def get_engine():
    """
    Get or create SQLAlchemy async engine (singleton)
    """
    global _engine
    
    if _engine is None:
        database_url = get_database_url()
        
        _engine = create_async_engine(
            database_url,
            pool_size=2,  # Small pool for Lambda
            max_overflow=0,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
    
    return _engine


def get_session_factory():
    """
    Get or create session factory (singleton)
    """
    global _session_factory
    
    if _session_factory is None:
        engine = get_engine()
        _session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    return _session_factory


@asynccontextmanager
async def get_db_session():
    """
    Get database session context manager
    """
    factory = get_session_factory()
    session = factory()
    
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
