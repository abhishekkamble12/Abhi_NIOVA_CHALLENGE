import logging
import json
import sys
import time
from datetime import datetime
from typing import Optional
from contextvars import ContextVar
from uuid import uuid4

from app.core.config import settings

# Context variables for request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "log_level": record.levelname,
            "service": settings.PROJECT_NAME,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add request_id if available
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id
        
        # Add user_id if available
        user_id = user_id_var.get()
        if user_id:
            log_data["user_id"] = user_id
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data)


def setup_logging():
    """Configure logging for the application"""
    
    # Determine log level based on environment
    log_level = logging.DEBUG if settings.is_development() else logging.INFO
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Use JSON formatter in production, simple format in development
    if settings.is_production():
        console_handler.setFormatter(JSONFormatter())
    else:
        # Human-readable format for development
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)
    
    root_logger.addHandler(console_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    **extra_fields
):
    """Log with additional context"""
    record = logger.makeRecord(
        logger.name,
        level,
        "(unknown file)",
        0,
        message,
        (),
        None
    )
    
    if request_id:
        request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)
    if extra_fields:
        record.extra_fields = extra_fields
    
    logger.handle(record)


def set_request_id(request_id: str):
    """Set request ID in context"""
    request_id_var.set(request_id)


def set_user_id(user_id: str):
    """Set user ID in context"""
    user_id_var.set(user_id)


def get_request_id() -> Optional[str]:
    """Get current request ID"""
    return request_id_var.get()


def get_user_id() -> Optional[str]:
    """Get current user ID"""
    return user_id_var.get()


# Initialize logging on module import
logger = setup_logging()
