# Logging Quick Reference

## Import

```python
from app.core.logging import get_logger, set_request_id, set_user_id

logger = get_logger(__name__)
```

## Basic Logging

```python
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)
logger.critical("Critical message")
```

## Logging with Extra Fields

```python
logger.info(
    "User action",
    extra={
        "extra_fields": {
            "user_id": "123",
            "action": "create_post",
            "post_id": 456
        }
    }
)
```

## Request Context

```python
# Set context (done automatically by middleware)
set_request_id("abc123")
set_user_id("user_456")

# All logs will include request_id and user_id
logger.info("Processing request")
```

## Route Example

```python
from fastapi import APIRouter, Request
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/items")
async def create_item(request: Request, data: dict):
    request_id = request.state.request_id
    
    logger.info("Creating item", extra={"extra_fields": {"name": data["name"]}})
    
    try:
        item = await db.create(data)
        logger.info("Item created", extra={"extra_fields": {"id": item.id}})
        return item
    except Exception as e:
        logger.error(f"Failed: {e}", exc_info=True)
        raise
```

## JSON Log Format

```json
{
  "timestamp": "2024-01-15T10:30:45.123456Z",
  "log_level": "INFO",
  "service": "AI Media OS - HiveMind",
  "message": "Request completed",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_id": "user_123",
  "method": "GET",
  "path": "/api/v1/articles",
  "status_code": 200,
  "duration_ms": 45.23
}
```

## Middleware Features

- ✅ Auto-generates request ID
- ✅ Logs incoming requests
- ✅ Logs response status
- ✅ Logs errors with stack traces
- ✅ Adds X-Request-ID header to responses
- ✅ Tracks request duration

## Environment Configuration

```bash
# Development: DEBUG level, human-readable
ENVIRONMENT=development

# Production: INFO level, JSON format
ENVIRONMENT=production
```

## Integration

### ELK Stack
```bash
python run.py | logstash -f logstash.conf
```

### Datadog
```bash
DD_SERVICE=hivemind ddtrace-run python run.py
```

### CloudWatch
```python
# Add watchtower handler in logging.py
import watchtower
```

## Files

- `app/core/logging.py` - Logging setup and JSON formatter
- `app/core/middleware.py` - Request logging middleware
- `LOGGING.md` - Full documentation
