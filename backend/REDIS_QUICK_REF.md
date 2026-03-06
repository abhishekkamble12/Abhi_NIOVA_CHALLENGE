# Redis Quick Reference

## Import

```python
from app.core.redis import (
    set_cache,
    get_cache,
    delete_cache,
    cache_feed,
    get_cached_feed,
    check_rate_limit,
    cache_ai_response,
    get_cached_ai_response
)
```

## Basic Operations

```python
# Set cache (auto JSON serialization)
await set_cache("key", {"data": "value"}, ttl=3600)

# Get cache (auto JSON deserialization)
data = await get_cache("key")

# Delete cache
await delete_cache("key")

# Delete pattern
await delete_pattern("user:*")
```

## Specialized Functions

```python
# Feed caching
await cache_feed(user_id=123, feed_data=[...], ttl=300)
feed = await get_cached_feed(user_id=123)

# AI response caching
await cache_ai_response(prompt_hash, response, ttl=3600)
cached = await get_cached_ai_response(prompt_hash)

# Rate limiting
can_proceed = await check_rate_limit(
    user_id=123,
    action="api_call",
    limit=100,
    window=3600
)

# Embedding caching
await cache_embeddings("article:123", embeddings, ttl=86400)
embeddings = await get_cached_embeddings("article:123")
```

## Route Example

```python
@router.get("/items/{id}")
async def get_item(id: int):
    # Check cache
    cached = await get_cache(f"item:{id}")
    if cached:
        return cached
    
    # Fetch from DB
    item = await db.get_item(id)
    
    # Cache result
    await set_cache(f"item:{id}", item, ttl=3600)
    return item
```

## Configuration

```bash
# .env
REDIS_URL=redis://localhost:6379/0
ENVIRONMENT=production  # Redis enabled
```

## Features

- ✅ Async redis-py client
- ✅ Connection pooling (10 connections)
- ✅ Retry logic (3 attempts)
- ✅ JSON serialization
- ✅ Graceful failure handling
- ✅ Optional in development

## Files

- `app/core/redis.py` - Redis infrastructure
- `REDIS.md` - Full documentation
