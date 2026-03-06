# Exception Handling Quick Reference

## Import

```python
from app.core.exceptions import (
    NotFoundException,
    UnauthorizedException,
    ValidationException,
    ServiceException
)
```

## Custom Exceptions

### NotFoundException (404)
```python
raise NotFoundException(
    message="Article not found",
    details={"article_id": 123}
)
```

### UnauthorizedException (401)
```python
raise UnauthorizedException(
    message="Invalid token",
    details={"token_status": "expired"}
)
```

### ValidationException (422)
```python
raise ValidationException(
    message="Validation failed",
    details={"errors": [{"field": "email", "message": "Invalid format"}]}
)
```

### ServiceException (503)
```python
raise ServiceException(
    message="External API error",
    details={"service": "payment-api", "error": "timeout"}
)
```

## Error Response Format

```json
{
  "error": {
    "type": "NotFound",
    "message": "Resource not found",
    "details": {}
  }
}
```

## Route Example

```python
from fastapi import APIRouter
from app.core.exceptions import NotFoundException

router = APIRouter()

@router.get("/items/{item_id}")
async def get_item(item_id: int):
    item = await db.get_item(item_id)
    
    if not item:
        raise NotFoundException(
            message=f"Item {item_id} not found",
            details={"item_id": item_id}
        )
    
    return item
```

## Status Codes

| Exception | Status Code |
|-----------|-------------|
| `NotFoundException` | 404 |
| `UnauthorizedException` | 401 |
| `ValidationException` | 422 |
| `ServiceException` | 503 |
| Unhandled | 500 |

## Features

- ✅ Standardized error format
- ✅ Automatic logging
- ✅ Stack traces hidden in production
- ✅ HTTP status code mapping
- ✅ FastAPI integration

## Files

- `app/core/exceptions.py` - Exception classes and handlers
- `app/examples/exception_examples.py` - Usage examples
- `EXCEPTIONS.md` - Full documentation
