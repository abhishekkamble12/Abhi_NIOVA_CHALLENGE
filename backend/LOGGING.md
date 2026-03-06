# Logging System Documentation

## Overview

Production-grade JSON logging system with request tracking, structured logging, and integration with monitoring platforms.

## Architecture

```
backend/app/core/
├── logging.py          # JSON formatter, context variables, setup
└── middleware.py       # Request logging middleware
```

## Key Features

✅ **Python logging module** - Standard library logging  
✅ **JSON format** - Structured logs for parsing  
✅ **Required fields** - timestamp, log_level, service, message, request_id, user_id  
✅ **Environment-based levels** - DEBUG in dev, INFO in prod  
✅ **Request logging middleware** - Automatic request/response logging  
✅ **Logs incoming requests** - Method, path, query params, client IP  
✅ **Logs response status** - Status code, duration  
✅ **Logs errors** - Exception info with stack traces  
✅ **FastAPI integration** - Middleware and lifecycle integration  
✅ **Ready for ingestion** - ELK, Datadog, CloudWatch compatible  

## Log Format

### JSON Structure (Production)

```json
{
  "timestamp": "2024-01-15T10:30:45.123456Z",
  "log_level": "INFO",
  "service": "AI Media OS - HiveMind",
  "message": "Request completed",
  "logger": "app.core.middleware",
  "module": "middleware",
  "function": "dispatch",
  "line": 45,
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_id": "user_123",
  "method": "GET",
  "path": "/api/v1/articles",
  "status_code": 200,
  "duration_ms": 45.23
}
```

### Human-Readable Format (Development)

```
2024-01-15 10:30:45 - app.core.middleware - INFO - Request completed
```

## Usage

### Basic Logging

```python
from app.core.logging import get_logger

logger = get_logger(__name__)

# Log levels
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

### Logging with Context

```python
from app.core.logging import log_with_context, get_logger

logger = get_logger(__name__)

log_with_context(
    logger,
    logging.INFO,
    "User action performed",
    request_id="abc123",
    user_id="user_456",
    action="create_post",
    post_id=789
)
```

### Request Context

```python
from app.core.logging import set_request_id, set_user_id, get_request_id

# Set context (usually done by middleware)
set_request_id("abc123")
set_user_id("user_456")

# Get context
request_id = get_request_id()
user_id = get_user_id()

# All subsequent logs will include these IDs
logger.info("Processing request")  # Includes request_id and user_id
```

## Request Logging Middleware

### Automatic Logging

The middleware automatically logs:

**Incoming Request:**
```json
{
  "timestamp": "2024-01-15T10:30:45.000000Z",
  "log_level": "INFO",
  "message": "Incoming request",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "method": "POST",
  "path": "/api/v1/articles",
  "query_params": "limit=10&offset=0",
  "client_ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0..."
}
```

**Successful Response:**
```json
{
  "timestamp": "2024-01-15T10:30:45.123456Z",
  "log_level": "INFO",
  "message": "Request completed",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "method": "POST",
  "path": "/api/v1/articles",
  "status_code": 201,
  "duration_ms": 123.45
}
```

**Error Response:**
```json
{
  "timestamp": "2024-01-15T10:30:45.123456Z",
  "log_level": "ERROR",
  "message": "Request failed: Database connection error",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "method": "POST",
  "path": "/api/v1/articles",
  "duration_ms": 50.12,
  "error": "Database connection error",
  "error_type": "DatabaseError",
  "exception": "Traceback (most recent call last)..."
}
```

### Request ID Header

The middleware adds `X-Request-ID` header to all responses:

```bash
curl -i http://localhost:8000/api/v1/articles
# Response includes:
# X-Request-ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### User ID Tracking

Pass user ID in request header:

```bash
curl -H "X-User-ID: user_123" http://localhost:8000/api/v1/articles
```

All logs for this request will include `"user_id": "user_123"`.

## Route-Level Logging

### Example Route

```python
from fastapi import APIRouter, Request
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/articles")
async def create_article(request: Request, data: dict):
    # Request ID is automatically available
    request_id = request.state.request_id
    
    logger.info(
        "Creating article",
        extra={"extra_fields": {"title": data.get("title")}}
    )
    
    try:
        article = await db.create_article(data)
        logger.info(
            "Article created successfully",
            extra={"extra_fields": {"article_id": article.id}}
        )
        return article
    
    except Exception as e:
        logger.error(
            f"Failed to create article: {str(e)}",
            exc_info=True
        )
        raise
```

## Log Levels by Environment

### Development
- **Level**: DEBUG
- **Format**: Human-readable
- **Output**: Console (stdout)
- **SQL Queries**: Logged

### Production
- **Level**: INFO
- **Format**: JSON
- **Output**: Console (stdout)
- **SQL Queries**: Not logged

### Configuration

```python
# Automatic based on ENVIRONMENT
ENVIRONMENT=development  # DEBUG level, human-readable
ENVIRONMENT=production   # INFO level, JSON format
```

## Integration with Monitoring Platforms

### ELK Stack (Elasticsearch, Logstash, Kibana)

**Logstash Configuration:**

```ruby
input {
  stdin {
    codec => json
  }
}

filter {
  json {
    source => "message"
  }
  
  date {
    match => ["timestamp", "ISO8601"]
    target => "@timestamp"
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "hivemind-logs-%{+YYYY.MM.dd}"
  }
}
```

**Run Application:**

```bash
python run.py | logstash -f logstash.conf
```

### Datadog

**Install Datadog Agent:**

```bash
pip install ddtrace
```

**Run with Datadog:**

```bash
DD_SERVICE=hivemind \
DD_ENV=production \
DD_LOGS_INJECTION=true \
ddtrace-run python run.py
```

**Datadog Configuration:**

```yaml
# datadog.yaml
logs_enabled: true
logs_config:
  container_collect_all: true
  processing_rules:
    - type: multi_line
      name: log_start_with_timestamp
      pattern: \d{4}-\d{2}-\d{2}
```

### AWS CloudWatch

**Install boto3:**

```bash
pip install boto3 watchtower
```

**Add CloudWatch Handler:**

```python
# In logging.py
import watchtower

def setup_cloudwatch_logging():
    if settings.is_production():
        cloudwatch_handler = watchtower.CloudWatchLogHandler(
            log_group="hivemind-api",
            stream_name="production"
        )
        cloudwatch_handler.setFormatter(JSONFormatter())
        logging.getLogger().addHandler(cloudwatch_handler)
```

**CloudWatch Insights Query:**

```sql
fields @timestamp, log_level, message, request_id, duration_ms
| filter log_level = "ERROR"
| sort @timestamp desc
| limit 100
```

## Performance Considerations

### Async Logging

For high-throughput applications:

```python
from logging.handlers import QueueHandler, QueueListener
import queue

def setup_async_logging():
    log_queue = queue.Queue()
    queue_handler = QueueHandler(log_queue)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    
    listener = QueueListener(log_queue, console_handler)
    listener.start()
    
    logging.getLogger().addHandler(queue_handler)
```

### Log Sampling

For very high traffic:

```python
import random

def should_log_request():
    # Log 10% of requests
    return random.random() < 0.1

# In middleware
if should_log_request():
    logger.info("Incoming request", ...)
```

## Security Best Practices

### Sensitive Data Filtering

```python
SENSITIVE_FIELDS = ["password", "token", "api_key", "secret"]

def sanitize_data(data: dict) -> dict:
    """Remove sensitive fields from logs"""
    return {
        k: "***REDACTED***" if k in SENSITIVE_FIELDS else v
        for k, v in data.items()
    }

# Usage
logger.info("User data", extra={"extra_fields": sanitize_data(user_data)})
```

### PII Masking

```python
import re

def mask_email(email: str) -> str:
    """Mask email addresses"""
    return re.sub(r'(.{2}).*(@.*)', r'\1***\2', email)

def mask_phone(phone: str) -> str:
    """Mask phone numbers"""
    return re.sub(r'\d(?=\d{4})', '*', phone)
```

## Troubleshooting

### Logs Not Appearing

```python
# Check log level
import logging
print(logging.getLogger().level)  # Should be 10 (DEBUG) or 20 (INFO)

# Force log output
logging.getLogger().setLevel(logging.DEBUG)
```

### JSON Parsing Errors

```python
# Validate JSON output
import json
log_output = '{"timestamp": "2024-01-15T10:30:45Z", ...}'
json.loads(log_output)  # Should not raise exception
```

### Missing Request ID

```python
# Ensure middleware is added
from app.core.middleware import RequestLoggingMiddleware
app.add_middleware(RequestLoggingMiddleware)
```

## Testing

### Test Logging

```python
import pytest
from app.core.logging import get_logger, set_request_id

def test_logging_with_request_id(caplog):
    logger = get_logger(__name__)
    set_request_id("test-123")
    
    logger.info("Test message")
    
    assert "test-123" in caplog.text
```

### Test Middleware

```python
from fastapi.testclient import TestClient
from app.main import app

def test_request_logging():
    client = TestClient(app)
    response = client.get("/api/v1/articles")
    
    # Check response header
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) == 36  # UUID length
```

## Example Queries

### Find Slow Requests

```bash
# Using jq
cat logs.json | jq 'select(.duration_ms > 1000)'
```

### Count Errors by Type

```bash
cat logs.json | jq -r 'select(.log_level == "ERROR") | .error_type' | sort | uniq -c
```

### Track User Activity

```bash
cat logs.json | jq 'select(.user_id == "user_123")'
```

## Summary

The logging system provides:
- ✅ Structured JSON logs for production
- ✅ Human-readable logs for development
- ✅ Automatic request/response tracking
- ✅ Request ID correlation
- ✅ User ID tracking
- ✅ Error logging with stack traces
- ✅ Ready for ELK, Datadog, CloudWatch
- ✅ Performance optimized
- ✅ Security-aware (PII masking ready)
