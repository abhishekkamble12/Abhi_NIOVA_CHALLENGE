"""Aurora PostgreSQL Service for EC2 in VPC"""
import asyncpg
from contextlib import asynccontextmanager
from functools import lru_cache
from config.aws_config import get_aws_settings

settings = get_aws_settings()

@lru_cache()
def get_connection_string() -> str:
    """Build PostgreSQL connection string"""
    return f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

@asynccontextmanager
async def get_db_connection():
    """Direct asyncpg connection to Aurora"""
    conn = await asyncpg.connect(get_connection_string())
    try:
        yield conn
    finally:
        await conn.close()

@asynccontextmanager
async def get_db_session():
    """Database session with transaction"""
    async with get_db_connection() as conn:
        async with conn.transaction():
            yield conn
