"""ElastiCache Redis Service for EC2 in VPC"""
import json
from typing import Optional, Any
from redis.asyncio import Redis
from functools import lru_cache
from config.aws_config import get_aws_settings

settings = get_aws_settings()

@lru_cache()
def get_redis_client() -> Redis:
    """Direct Redis connection to ElastiCache"""
    return Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
        db=settings.REDIS_DB,
        ssl=settings.REDIS_SSL,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_keepalive=True
    )

class CacheService:
    def __init__(self):
        self.client = get_redis_client()
    
    async def ping(self) -> bool:
        """Test Redis connection"""
        return await self.client.ping()
    
    async def get(self, key: str) -> Optional[Any]:
        value = await self.client.get(key)
        return json.loads(value) if value else None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        await self.client.setex(key, ttl, json.dumps(value))
    
    async def delete(self, key: str):
        await self.client.delete(key)
    
    async def get_embedding(self, text: str) -> Optional[list]:
        return await self.get(f"embedding:{hash(text)}")
    
    async def set_embedding(self, text: str, embedding: list):
        await self.set(f"embedding:{hash(text)}", embedding, settings.CACHE_TTL_EMBEDDING)
    
    async def get_feed(self, user_id: int) -> Optional[list]:
        return await self.get(f"feed:{user_id}")
    
    async def set_feed(self, user_id: int, articles: list):
        await self.set(f"feed:{user_id}", articles, settings.CACHE_TTL_FEED)

@lru_cache()
def get_cache_service() -> CacheService:
    return CacheService()
