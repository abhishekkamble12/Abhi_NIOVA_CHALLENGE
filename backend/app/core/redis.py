from redis.asyncio import Redis, ConnectionPool
from typing import Optional, Any
import json
import logging
from functools import wraps

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global Redis client
redis_client: Optional[Redis] = None
connection_pool: Optional[ConnectionPool] = None


async def init_redis() -> Optional[Redis]:
    """Initialize Redis connection pool and client"""
    global redis_client, connection_pool
    
    if not settings.REDIS_URL or settings.is_development():
        logger.info("Redis disabled in development mode")
        return None
    
    try:
        connection_pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=10,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True,
            retry_on_timeout=True,
        )
        
        redis_client = Redis(connection_pool=connection_pool)
        await redis_client.ping()
        logger.info("Redis connected successfully")
        return redis_client
    
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Continuing without Redis.")
        redis_client = None
        return None


async def close_redis():
    """Close Redis connection"""
    global redis_client, connection_pool
    
    if redis_client:
        await redis_client.aclose()
        logger.info("Redis connection closed")
    
    if connection_pool:
        await connection_pool.aclose()


async def get_redis() -> Optional[Redis]:
    """Get Redis client instance"""
    return redis_client


def redis_retry(max_retries: int = 3):
    """Decorator for Redis operations with retry logic"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not redis_client:
                return None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Redis operation failed after {max_retries} attempts: {e}")
                        return None
                    logger.warning(f"Redis operation failed (attempt {attempt + 1}/{max_retries}): {e}")
            return None
        return wrapper
    return decorator


@redis_retry(max_retries=3)
async def set_cache(key: str, value: Any, ttl: int = 3600) -> bool:
    """Set cache with JSON serialization and TTL"""
    if not redis_client:
        return False
    
    serialized = json.dumps(value) if not isinstance(value, str) else value
    await redis_client.setex(key, ttl, serialized)
    return True


@redis_retry(max_retries=3)
async def get_cache(key: str) -> Optional[Any]:
    """Get cache with JSON deserialization"""
    if not redis_client:
        return None
    
    value = await redis_client.get(key)
    if value is None:
        return None
    
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


@redis_retry(max_retries=3)
async def delete_cache(key: str) -> bool:
    """Delete cache key"""
    if not redis_client:
        return False
    
    await redis_client.delete(key)
    return True


@redis_retry(max_retries=3)
async def delete_pattern(pattern: str) -> int:
    """Delete all keys matching pattern"""
    if not redis_client:
        return 0
    
    keys = await redis_client.keys(pattern)
    if keys:
        return await redis_client.delete(*keys)
    return 0


# ============================================================================
# SPECIALIZED CACHE FUNCTIONS FOR FUTURE USE
# ============================================================================

async def cache_feed(user_id: int, feed_data: list, ttl: int = 300):
    """Cache personalized news feed"""
    return await set_cache(f"feed:{user_id}", feed_data, ttl)


async def get_cached_feed(user_id: int) -> Optional[list]:
    """Get cached news feed"""
    return await get_cache(f"feed:{user_id}")


async def cache_ai_response(prompt_hash: str, response: dict, ttl: int = 3600):
    """Cache AI API responses to reduce costs"""
    return await set_cache(f"ai:{prompt_hash}", response, ttl)


async def get_cached_ai_response(prompt_hash: str) -> Optional[dict]:
    """Get cached AI response"""
    return await get_cache(f"ai:{prompt_hash}")


async def check_rate_limit(user_id: int, action: str, limit: int = 100, window: int = 3600) -> bool:
    """Check if user exceeded rate limit"""
    if not redis_client:
        return True  # Allow if Redis unavailable
    
    key = f"ratelimit:{user_id}:{action}"
    
    try:
        current = await redis_client.incr(key)
        if current == 1:
            await redis_client.expire(key, window)
        
        return current <= limit
    except Exception as e:
        logger.error(f"Rate limit check failed: {e}")
        return True  # Allow on error


async def cache_embeddings(content_id: str, embeddings: list[float], ttl: int = 86400):
    """Cache vector embeddings"""
    return await set_cache(f"embedding:{content_id}", embeddings, ttl)


async def get_cached_embeddings(content_id: str) -> Optional[list[float]]:
    """Get cached embeddings"""
    return await get_cache(f"embedding:{content_id}")


# ============================================================================
# LEGACY MOCK CODE (COMMENTED OUT - DO NOT REMOVE)
# ============================================================================
# class MockRedis:
#     def ping(self):
#         return True
#     
#     def close(self):
#         pass
#
# redis_client = MockRedis()
# ============================================================================
