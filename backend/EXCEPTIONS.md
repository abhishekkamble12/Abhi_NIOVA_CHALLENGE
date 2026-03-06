# Exception Handling Documentation

## Overview

Global exception handling system with custom exceptions, standardized error responses, and automatic logging.

## Architecture

```
backend/app/core/exceptions.py
├── Custom Exception Classes
│   ├── BaseAPIException
│   ├── NotFoundException (404)
│   ├── UnauthorizedException (401)
│   ├── ValidationException (422)
│   └── ServiceException (503)
├── Error Response Formatter
└── Exception Handlers
    ├── base_api_exception_handler
    ├── http_exception_handler
    ├── validation_exception_handler
    └── generic_exception_handler
```

## Key Features

✅ **Custom exception classes** - NotFoundException, UnauthorizedException, ValidationException, ServiceException  
✅ **Standardized error format** - Consistent JSON structure  
✅ **FastAPI exception handlers** - Automatic error handling  
✅ **Logging integration** - All errors logged with context  
✅ **HTTP status code mapping** - Correct status codes  
✅ **Stack traces hidden in production** - Security best practice  

## Custom Exception Classes

### BaseAPIException

Base class for all custom exceptions:

```python
class BaseAPIException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_type: str = "InternalServerError",
        details: Optional[Dict[str, Any]] = None
    ):
        ...
```

### NotFoundException (404)

```python
from app.core.exceptions import NotFoundException

raise NotFoundException(
    message="Article not found",
    details={"article_id": 123}
)
```

**Response:**
```json
{
  "error": {
    "type": "NotFound",
    "message": "Article not found",
    "details": {
      "article_id": 123
    }
  }
}
```

### UnauthorizedException (401)

```python
from app.core.exceptions import UnauthorizedException

raise UnauthorizedException(
    message="Invalid token",
    details={"token_status": "expired"}
)
```

**Response:**
```json
{
  "error": {
    "type": "Unauthorized",
    "message": "Invalid token",
    "details": {
      "token_status": "expired"
    }
  }
}
```

### ValidationException (422)

```python
from app.core.exceptions import ValidationException

raise ValidationException(
    message="Validation failed",
    details={
        "errors": [
            {"field": "email", "message": "Invalid email format"},
            {"field": "password", "message": "Password too short"}
        ]
    }
)
```

**Response:**
```json
{
  "error": {
    "type": "ValidationError",
    "message": "Validation failed",
    "details": {
      "errors": [
        {"field": "email", "message": "Invalid email format"},
        {"field": "password", "message": "Password too short"}
      ]
    }
  }
}
```

### ServiceException (503)

```python
from app.core.exceptions import ServiceException

raise ServiceException(
    message="External API unavailable",
    details={
        "service": "payment-gateway",
        "error": "timeout"
    }
)
```

**Response:**
```json
{
  "error": {
    "type": "ServiceError",
    "message": "External API unavailable",
    "details": {
      "service": "payment-gateway",
      "error": "timeout"
    }
  }
}
```

## Standardized Error Format

All errors follow this structure:

```json
{
  "error": {
    "type": "ErrorType",
    "message": "Human-readable error message",
    "details": {
      "additional": "context",
      "field": "value"
    }
  }
}
```

### Development Mode

In development, stack traces are included:

```json
{
  "error": {
    "type": "DatabaseError",
    "message": "Connection failed",
    "details": {
      "traceback": "Traceback (most recent call last):\n  File..."
    }
  }
}
```

### Production Mode

In production, stack traces are hidden:

```json
{
  "error": {
    "type": "InternalServerError",
    "message": "An internal server error occurred",
    "details": {}
  }
}
```

## Usage in Routes

### Basic Usage

```python
from fastapi import APIRouter
from app.core.exceptions import NotFoundException

router = APIRouter()

@router.get("/articles/{article_id}")
async def get_article(article_id: int):
    article = await db.get_article(article_id)
    
    if not article:
        raise NotFoundException(
            message=f"Article {article_id} not found",
            details={"article_id": article_id}
        )
    
    return article
```

### With Authentication

```python
from app.core.exceptions import UnauthorizedException

@router.get("/admin/users")
async def get_users(token: str):
    if not verify_token(token):
        raise UnauthorizedException(
            message="Invalid or expired token",
            details={"token_status": "invalid"}
        )
    
    return await db.get_users()
```

### With Validation

```python
from app.core.exceptions import ValidationException

@router.post("/articles")
async def create_article(data: dict):
    errors = []
    
    if not data.get("title"):
        errors.append({"field": "title", "message": "Title is required"})
    
    if not data.get("content"):
        errors.append({"field": "content", "message": "Content is required"})
    
    if errors:
        raise ValidationException(
            message="Validation failed",
            details={"errors": errors}
        )
    
    return await db.create_article(data)
```

### With External Services

```python
from app.core.exceptions import ServiceException
import httpx

@router.post("/process")
async def process_data(data: dict):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.example.com", json=data)
            response.raise_for_status()
    
    except httpx.TimeoutException:
        raise ServiceException(
            message="External service timeout",
            details={"service": "example-api", "timeout": 5}
        )
    
    except httpx.HTTPError as e:
        raise ServiceException(
            message="External service error",
            details={"service": "example-api", "error": str(e)}
        )
    
    return {"status": "processed"}
```

## Exception Handlers

### Custom Exception Handler

Handles all `BaseAPIException` subclasses:

```python
async def base_api_exception_handler(request: Request, exc: BaseAPIException):
    # Logs error with context
    # Returns standardized JSON response
    ...
```

### HTTP Exception Handler

Handles FastAPI/Starlette HTTP exceptions:

```python
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Converts HTTP exceptions to standard format
    ...
```

### Validation Exception Handler

Handles Pydantic validation errors:

```python
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Formats validation errors
    # Returns 422 status code
    ...
```

### Generic Exception Handler

Catches all unhandled exceptions:

```python
async def generic_exception_handler(request: Request, exc: Exception):
    # Logs full stack trace
    # Hides details in production
    # Returns 500 status code
    ...
```

## HTTP Status Code Mapping

| Exception | Status Code | Description |
|-----------|-------------|-------------|
| `NotFoundException` | 404 | Resource not found |
| `UnauthorizedException` | 401 | Authentication required |
| `ValidationException` | 422 | Validation failed |
| `ServiceException` | 503 | External service error |
| `HTTPException` | Variable | HTTP errors |
| `RequestValidationError` | 422 | Pydantic validation |
| `Exception` | 500 | Unhandled errors |

## Logging Integration

All exceptions are automatically logged:

### Custom Exceptions

```json
{
  "timestamp": "2024-01-15T10:30:45Z",
  "log_level": "ERROR",
  "message": "NotFound: Article not found",
  "error_type": "NotFound",
  "status_code": 404,
  "path": "/api/v1/articles/123",
  "method": "GET",
  "details": {"article_id": 123}
}
```

### Validation Errors

```json
{
  "timestamp": "2024-01-15T10:30:45Z",
  "log_level": "WARNING",
  "message": "Validation error: 2 field(s) failed validation",
  "path": "/api/v1/articles",
  "method": "POST",
  "errors": [
    {"field": "title", "message": "field required", "type": "value_error.missing"}
  ]
}
```

### Unhandled Exceptions

```json
{
  "timestamp": "2024-01-15T10:30:45Z",
  "log_level": "ERROR",
  "message": "Unhandled exception: division by zero",
  "error_type": "ZeroDivisionError",
  "path": "/api/v1/calculate",
  "method": "POST",
  "exception": "Traceback (most recent call last)..."
}
```

## Testing

### Test Custom Exceptions

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_not_found_exception():
    response = client.get("/api/v1/articles/999999")
    
    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "type": "NotFound",
            "message": "Article not found",
            "details": {"article_id": 999999}
        }
    }

def test_validation_exception():
    response = client.post("/api/v1/articles", json={})
    
    assert response.status_code == 422
    assert "error" in response.json()
    assert response.json()["error"]["type"] == "ValidationError"
```

### Test Error Logging

```python
def test_exception_logging(caplog):
    from app.core.exceptions import NotFoundException
    
    with pytest.raises(NotFoundException):
        raise NotFoundException("Test error")
    
    # Verify error was logged
    assert "NotFound" in caplog.text
```

## Best Practices

### 1. Use Specific Exceptions

```python
# ✅ Good
raise NotFoundException(message="Article not found", details={"id": 123})

# ❌ Bad
raise Exception("Not found")
```

### 2. Provide Helpful Details

```python
# ✅ Good
raise ValidationException(
    message="Invalid input",
    details={
        "errors": [
            {"field": "email", "message": "Invalid format"},
            {"field": "age", "message": "Must be positive"}
        ]
    }
)

# ❌ Bad
raise ValidationException(message="Invalid")
```

### 3. Don't Expose Sensitive Information

```python
# ✅ Good
raise UnauthorizedException(
    message="Authentication failed",
    details={"reason": "invalid_credentials"}
)

# ❌ Bad
raise UnauthorizedException(
    message="Password 'secret123' is incorrect for user@example.com"
)
```

### 4. Re-raise Custom Exceptions

```python
# ✅ Good
try:
    article = await get_article(id)
except NotFoundException:
    raise  # Re-raise custom exceptions

# ❌ Bad
try:
    article = await get_article(id)
except NotFoundException as e:
    raise Exception(str(e))  # Loses exception type
```

## Security Considerations

### Production Mode

- Stack traces are hidden
- Generic error messages for unhandled exceptions
- Sensitive data filtered from logs

### Development Mode

- Full stack traces included
- Detailed error messages
- Helpful debugging information

### Configuration

```python
# Automatic based on ENVIRONMENT
ENVIRONMENT=production  # Hides stack traces
ENVIRONMENT=development # Shows stack traces
```

## Summary

The exception handling system provides:
- ✅ 4 custom exception classes
- ✅ Standardized JSON error format
- ✅ Automatic logging with context
- ✅ Correct HTTP status codes
- ✅ Stack traces hidden in production
- ✅ FastAPI integration
- ✅ Easy to use and extend
