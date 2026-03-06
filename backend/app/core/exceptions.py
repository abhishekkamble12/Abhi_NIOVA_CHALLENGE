from typing import Optional, Dict, Any
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


# ============================================================================
# CUSTOM EXCEPTION CLASSES
# ============================================================================

class BaseAPIException(Exception):
    """Base exception for all API exceptions"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_type: str = "InternalServerError",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(BaseAPIException):
    """Resource not found exception"""
    
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_type="NotFound",
            details=details
        )


class UnauthorizedException(BaseAPIException):
    """Unauthorized access exception"""
    
    def __init__(self, message: str = "Unauthorized", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_type="Unauthorized",
            details=details
        )


class ValidationException(BaseAPIException):
    """Validation error exception"""
    
    def __init__(self, message: str = "Validation error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_type="ValidationError",
            details=details
        )


class ServiceException(BaseAPIException):
    """External service error exception"""
    
    def __init__(self, message: str = "Service error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_type="ServiceError",
            details=details
        )


# ============================================================================
# ERROR RESPONSE FORMATTER
# ============================================================================

def create_error_response(
    error_type: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
) -> JSONResponse:
    """Create standardized error response"""
    
    error_response = {
        "error": {
            "type": error_type,
            "message": message,
            "details": details or {}
        }
    }
    
    # Add stack trace in development mode only
    if settings.is_development() and details and "traceback" in details:
        error_response["error"]["traceback"] = details["traceback"]
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

async def base_api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """Handle custom API exceptions"""
    
    logger.error(
        f"{exc.error_type}: {exc.message}",
        extra={
            "extra_fields": {
                "error_type": exc.error_type,
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method,
                "details": exc.details
            }
        }
    )
    
    return create_error_response(
        error_type=exc.error_type,
        message=exc.message,
        details=exc.details,
        status_code=exc.status_code
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    
    logger.warning(
        f"HTTP {exc.status_code}: {exc.detail}",
        extra={
            "extra_fields": {
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method
            }
        }
    )
    
    return create_error_response(
        error_type="HTTPError",
        message=str(exc.detail),
        status_code=exc.status_code
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors"""
    
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation error: {len(errors)} field(s) failed validation",
        extra={
            "extra_fields": {
                "path": request.url.path,
                "method": request.method,
                "errors": errors
            }
        }
    )
    
    return create_error_response(
        error_type="ValidationError",
        message="Request validation failed",
        details={"errors": errors},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions"""
    
    import traceback
    
    # Log full error with stack trace
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={
            "extra_fields": {
                "error_type": type(exc).__name__,
                "path": request.url.path,
                "method": request.method
            }
        }
    )
    
    # Hide details in production
    if settings.is_production():
        return create_error_response(
            error_type="InternalServerError",
            message="An internal server error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    else:
        # Show details in development
        return create_error_response(
            error_type=type(exc).__name__,
            message=str(exc),
            details={"traceback": traceback.format_exc()},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# EXCEPTION HANDLER REGISTRATION
# ============================================================================

def register_exception_handlers(app):
    """Register all exception handlers with FastAPI app"""
    
    # Custom exceptions
    app.add_exception_handler(BaseAPIException, base_api_exception_handler)
    
    # HTTP exceptions
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # Validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # Generic exceptions (catch-all)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("Exception handlers registered")
