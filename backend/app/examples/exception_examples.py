"""
Example usage of custom exceptions in routes
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import (
    NotFoundException,
    UnauthorizedException,
    ValidationException,
    ServiceException
)

router = APIRouter()


# ============================================================================
# EXAMPLE 1: NotFoundException
# ============================================================================

@router.get("/articles/{article_id}")
async def get_article(article_id: int, db: AsyncSession = Depends(get_db)):
    """Example of NotFoundException"""
    
    # Simulate database query
    article = None  # await db.get(Article, article_id)
    
    if not article:
        raise NotFoundException(
            message=f"Article with ID {article_id} not found",
            details={"article_id": article_id}
        )
    
    return article


# ============================================================================
# EXAMPLE 2: UnauthorizedException
# ============================================================================

@router.get("/admin/users")
async def get_users(authorization: str = None):
    """Example of UnauthorizedException"""
    
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedException(
            message="Missing or invalid authorization token",
            details={"required": "Bearer token"}
        )
    
    # Verify token
    token = authorization.replace("Bearer ", "")
    if token != "valid_token":
        raise UnauthorizedException(
            message="Invalid or expired token",
            details={"token_status": "invalid"}
        )
    
    return {"users": []}


# ============================================================================
# EXAMPLE 3: ValidationException
# ============================================================================

@router.post("/articles")
async def create_article(data: dict):
    """Example of ValidationException"""
    
    # Custom validation
    if not data.get("title"):
        raise ValidationException(
            message="Title is required",
            details={"field": "title", "constraint": "required"}
        )
    
    if len(data.get("title", "")) < 5:
        raise ValidationException(
            message="Title must be at least 5 characters",
            details={
                "field": "title",
                "constraint": "min_length",
                "min_length": 5,
                "actual_length": len(data.get("title", ""))
            }
        )
    
    return {"id": 123, **data}


# ============================================================================
# EXAMPLE 4: ServiceException
# ============================================================================

import httpx

@router.post("/articles/{article_id}/publish")
async def publish_article(article_id: int):
    """Example of ServiceException"""
    
    try:
        # Call external service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.external-service.com/publish",
                json={"article_id": article_id},
                timeout=5.0
            )
            response.raise_for_status()
    
    except httpx.TimeoutException:
        raise ServiceException(
            message="External service timeout",
            details={
                "service": "external-service",
                "error": "timeout",
                "timeout_seconds": 5
            }
        )
    
    except httpx.HTTPError as e:
        raise ServiceException(
            message="External service error",
            details={
                "service": "external-service",
                "error": str(e),
                "status_code": getattr(e.response, "status_code", None)
            }
        )
    
    return {"status": "published"}


# ============================================================================
# EXAMPLE 5: Multiple Validation Errors
# ============================================================================

@router.post("/users")
async def create_user(data: dict):
    """Example of ValidationException with multiple errors"""
    
    errors = []
    
    if not data.get("email"):
        errors.append({"field": "email", "message": "Email is required"})
    elif "@" not in data.get("email", ""):
        errors.append({"field": "email", "message": "Invalid email format"})
    
    if not data.get("password"):
        errors.append({"field": "password", "message": "Password is required"})
    elif len(data.get("password", "")) < 8:
        errors.append({"field": "password", "message": "Password must be at least 8 characters"})
    
    if errors:
        raise ValidationException(
            message="User validation failed",
            details={"errors": errors}
        )
    
    return {"id": 456, "email": data["email"]}


# ============================================================================
# EXAMPLE 6: Nested Exception Handling
# ============================================================================

async def get_article_from_db(article_id: int):
    """Helper function that may raise exceptions"""
    
    # Simulate database error
    if article_id < 0:
        raise ValueError("Invalid article ID")
    
    # Simulate not found
    if article_id > 1000:
        raise NotFoundException(
            message=f"Article {article_id} not found",
            details={"article_id": article_id}
        )
    
    return {"id": article_id, "title": "Example Article"}


@router.get("/articles/{article_id}/details")
async def get_article_details(article_id: int):
    """Example of handling nested exceptions"""
    
    try:
        article = await get_article_from_db(article_id)
        return article
    
    except NotFoundException:
        # Re-raise custom exceptions
        raise
    
    except ValueError as e:
        # Convert to ValidationException
        raise ValidationException(
            message=str(e),
            details={"article_id": article_id}
        )
    
    except Exception as e:
        # Convert unknown errors to ServiceException
        raise ServiceException(
            message="Failed to fetch article",
            details={"error": str(e)}
        )
