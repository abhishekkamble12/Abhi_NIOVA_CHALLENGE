# Redis Infrastructure Documentation

## Overview

Production-grade async Redis client with connection pooling, retry logic, and specialized caching functions.

## Architecture

```
backend/app/core/redis.py
├── Connection Pool (max 10 connections)
├── Async Redis Client
├── Retry Logic (3 attempts)
├── JSON Serialization
├── Helper Functions
│   ├── set_cache()
│   ├── get_cache()
│   ├── delete_cache()
│   └── delete_pattern()
└── Specialized Functions
    ├── Feed Caching
    ├── AI Response Caching
    ├── Rate Limiting
    └── Embedding Caching
```

## Key Features

✅ **redis-py async client** - Full async/await support  
✅ **Connection pooling** - Max 10 connections with keepalive  
✅ **Global Redis client** - Singleton pattern  
✅ **Configuration from settings** - Uses settings.REDIS_URL  
✅ **Helper functions** - get_redis(), set_cache(), get_cache(), delete_cache()  
✅ **JSON serialization** - Automatic JSON encoding/decoding  
✅ **Graceful failure handling** - Returns None on errors  
✅ **Retry logic** - 3 attempts with exponential backoff  
✅ **Optional in development** - Disabled by default in dev mode  
✅ **Future-ready** - Feed caching, rate limiting, AI caching, background jobs  

## Configuration

### Redis URL Format

```bash
# .env
REDIS_URL=redis://localhost:6379/0

# With password
REDIS_URL=redis://:password@localhost:6379/0

# Redis Cluster
REDIS_URL=redis://host1:6379,host2:6379,host3:6379/0

# Redis Sentinel
REDIS_URL=redis+sentinel://sentinel1:26379,sentinel2:26379/mymaster/0
```

### Connection Pool Settings

```python
max_connections=10           # Maximum connections
decode_responses=True        # Auto-decode to strings
socket_connect_timeout=5     # Connection timeout
socket_keepalive=True        # Keep connections alive
retry_on_timeout=True        # Retry on timeout
```

## Basic Usage

### Import

```python
from app.core.redis import (
    get_redis,
    set_cache,
    get_cache,
    delete_cache,
    delete_pattern
)
```

### Set Cache

```python
# Simple string
await set_cache("key", "value", ttl=3600)

# JSON object
await set_cache("user:123", {"name": "John", "age": 30}, ttl=3600)

# List
await set_cache("items", [1, 2, 3, 4, 5], ttl=300)
```

### Get Cache

```python
# Returns None if not found
value = await get_cache("key")

# Automatic JSON deserialization
user = await get_cache("user:123")  # Returns dict
```

### Delete Cache

```python
# Delete single key
await delete_cache("key")

# Delete pattern
await delete_pattern("user:*")  # Deletes all user keys
```

## Advanced Usage

### Direct Redis Client

```python
from app.core.redis import get_redis

redis = await get_redis()
if redis:
    # Use any redis-py command
    await redis.set("key", "value")
    await redis.expire("key", 3600)
    await redis.lpush("list", "item")
    await redis.sadd("set", "member")
```

### Custom Retry Logic

```python
from app.core.redis import redis_retry

@redis_retry(max_retries=5)
async def my_redis_operation():
    redis = await get_redis()
    return await redis.get("key")
```

## Specialized Functions

### Feed Caching

```python
from app.core.redis import cache_feed, get_cached_feed

# Cache user's personalized feed
await cache_feed(user_id=123, feed_data=[...], ttl=300)

# Retrieve cached feed
feed = await get_cached_feed(user_id=123)
```

### AI Response Caching

```python
from app.core.redis import cache_ai_response, get_cached_ai_response
import hashlib

# Generate hash from prompt
prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()

# Check cache first
cached = await get_cached_ai_response(prompt_hash)
if cached:
    return cached

# Call AI API
response = await openai_call(prompt)

# Cache response
await cache_ai_response(prompt_hash, response, ttl=3600)
```

### Rate Limiting

```python
from app.core.redis import check_rate_limit

# Check if user can perform action
can_proceed = await check_rate_limit(
    user_id=123,
    action="api_call",
    limit=100,      # 100 requests
    window=3600     # per hour
)

if not can_proceed:
    raise HTTPException(status_code=429, detail="Rate limit exceeded")
```

### Embedding Caching

```python
from app.core.redis import cache_embeddings, get_cached_embeddings

# Check cache first
embeddings = await get_cached_embeddings(content_id="article:123")
if embeddings:
    return embeddings

# Generate embeddings
embeddings = model.encode(text)

# Cache for 24 hours
await cache_embeddings("article:123", embeddings.tolist(), ttl=86400)
```

## FastAPI Integration

### Route Example

```python
from fastapi import APIRouter, Depends
from app.core.redis import get_cache, set_cache

router = APIRouter()

@router.get("/articles/{article_id}")
async def get_article(article_id: int):
    # Check cache first
    cached = await get_cache(f"article:{article_id}")
    if cached:
        return cached
    
    # Fetch from database
    article = await db.get_article(article_id)
    
    # Cache for 1 hour
    await set_cache(f"article:{article_id}", article, ttl=3600)
    
    return article
```

### Cache Invalidation

```python
@router.put("/articles/{article_id}")
async def update_article(article_id: int, data: dict):
    # Update database
    article = await db.update_article(article_id, data)
    
    # Invalidate cache
    await delete_cache(f"article:{article_id}")
    
    return article
```

## Error Handling

### Graceful Degradation

```python
# All functions return None on failure
value = await get_cache("key")
if value is None:
    # Either key doesn't exist or Redis is down
    # Fetch from database as fallback
    value = await db.get_value()
```

### Check Redis Availability

```python
from app.core.redis import get_redis

redis = await get_redis()
if redis is None:
    # Redis is unavailable
    # Use alternative caching or skip caching
    pass
```

## Performance Optimization

### Batch Operations

```python
redis = await get_redis()
if redis:
    # Use pipeline for multiple operations
    async with redis.pipeline() as pipe:
        pipe.set("key1", "value1")
        pipe.set("key2", "value2")
        pipe.set("key3", "value3")
        await pipe.execute()
```

### TTL Strategy

```python
# Short TTL for frequently changing data
await set_cache("trending", data, ttl=60)  # 1 minute

# Medium TTL for semi-static data
await set_cache("feed:123", data, ttl=300)  # 5 minutes

# Long TTL for static data
await set_cache("config", data, ttl=3600)  # 1 hour

# Very long TTL for embeddings
await cache_embeddings("article:123", embeddings, ttl=86400)  # 24 hours
```

## Monitoring

### Health Check

```python
from app.core.redis import get_redis

@app.get("/health")
async def health_check():
    redis = await get_redis()
    redis_status = "connected" if redis else "disconnected"
    
    return {
        "redis": redis_status
    }
```

### Cache Hit Rate

```python
# Track cache hits/misses
cache_hits = 0
cache_misses = 0

value = await get_cache("key")
if value:
    cache_hits += 1
else:
    cache_misses += 1

hit_rate = cache_hits / (cache_hits + cache_misses)
```

## Development Mode

Redis is automatically disabled in development mode:

```bash
# .env
ENVIRONMENT=development  # Redis disabled
ENVIRONMENT=production   # Redis enabled
```

Override in development:

```python
# Force enable Redis in development
if settings.is_development():
    await init_redis()  # Will still try to connect
```

## Production Deployment

### Redis Configuration

```bash
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
timeout 300
tcp-keepalive 60
```

### Docker Compose

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    
volumes:
  redis_data:
```

### AWS ElastiCache

```bash
# .env
REDIS_URL=redis://your-cluster.cache.amazonaws.com:6379/0
```

## Troubleshooting

### Connection Refused

```bash
# Check if Redis is running
redis-cli ping

# Start Redis
redis-server

# Or with Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### Timeout Errors

```python
# Increase timeout in redis.py
socket_connect_timeout=10  # Increase from 5 to 10
```

### Memory Issues

```bash
# Check memory usage
redis-cli INFO memory

# Set eviction policy
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## Security Best Practices

1. **Use password authentication**
   ```bash
   REDIS_URL=redis://:strong_password@localhost:6379/0
   ```

2. **Enable SSL/TLS in production**
   ```bash
   REDIS_URL=rediss://host:6380/0
   ```

3. **Restrict network access**
   - Bind to localhost in development
   - Use VPC in production

4. **Disable dangerous commands**
   ```bash
   # redis.conf
   rename-command FLUSHDB ""
   rename-command FLUSHALL ""
   ```

## Testing

### Mock Redis for Tests

```python
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
async def mock_redis(monkeypatch):
    mock = AsyncMock()
    monkeypatch.setattr("app.core.redis.redis_client", mock)
    return mock

async def test_cache(mock_redis):
    mock_redis.get.return_value = '{"key": "value"}'
    result = await get_cache("test")
    assert result == {"key": "value"}
```

## Migration from Mock

All legacy mock code is preserved as comments in redis.py. The new implementation is production-ready and backward compatible.
