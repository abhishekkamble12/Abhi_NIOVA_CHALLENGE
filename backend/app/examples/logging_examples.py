"""
Example usage of the logging system in routes and services
"""

from fastapi import APIRouter, Request, HTTPException
from app.core.logging import get_logger, set_user_id
import time

router = APIRouter()
logger = get_logger(__name__)


# ============================================================================
# EXAMPLE 1: Basic Route Logging
# ============================================================================

@router.get("/articles/{article_id}")
async def get_article(article_id: int, request: Request):
    """Example of basic logging in a route"""
    
    # Request ID is automatically available from middleware
    request_id = request.state.request_id
    
    logger.info(
        f"Fetching article {article_id}",
        extra={"extra_fields": {"article_id": article_id}}
    )
    
    # Simulate database call
    article = {"id": article_id, "title": "Example Article"}
    
    return article


# ============================================================================
# EXAMPLE 2: Error Logging
# ============================================================================

@router.post("/articles")
async def create_article(data: dict, request: Request):
    """Example of error logging with exception info"""
    
    logger.info(
        "Creating new article",
        extra={"extra_fields": {"title": data.get("title")}}
    )
    
    try:
        # Simulate validation error
        if not data.get("title"):
            raise ValueError("Title is required")
        
        # Simulate database operation
        article = {"id": 123, **data}
        
        logger.info(
            "Article created successfully",
            extra={"extra_fields": {"article_id": 123}}
        )
        
        return article
    
    except ValueError as e:
        logger.warning(
            f"Validation error: {str(e)}",
            extra={"extra_fields": {"error": str(e)}}
        )
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(
            f"Failed to create article: {str(e)}",
            exc_info=True,  # Include full stack trace
            extra={"extra_fields": {"error_type": type(e).__name__}}
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================================
# EXAMPLE 3: User Context Logging
# ============================================================================

@router.get("/user/profile")
async def get_user_profile(request: Request):
    """Example of logging with user context"""
    
    # Extract user ID from auth token (example)
    user_id = request.headers.get("X-User-ID", "anonymous")
    
    # Set user context for all subsequent logs
    set_user_id(user_id)
    
    logger.info(
        "Fetching user profile",
        extra={"extra_fields": {"user_id": user_id}}
    )
    
    # All logs from here will include user_id
    profile = {"user_id": user_id, "name": "John Doe"}
    
    logger.info("Profile fetched successfully")
    
    return profile


# ============================================================================
# EXAMPLE 4: Service Layer Logging
# ============================================================================

class ArticleService:
    """Example service with logging"""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    async def create_article(self, data: dict) -> dict:
        """Create article with detailed logging"""
        
        self.logger.debug(
            "Validating article data",
            extra={"extra_fields": {"data_keys": list(data.keys())}}
        )
        
        # Validation
        if not data.get("title"):
            self.logger.warning("Article validation failed: missing title")
            raise ValueError("Title is required")
        
        self.logger.info(
            "Creating article in database",
            extra={"extra_fields": {"title": data["title"]}}
        )
        
        # Database operation
        article = {"id": 123, **data}
        
        self.logger.info(
            "Article created successfully",
            extra={"extra_fields": {"article_id": 123}}
        )
        
        return article
