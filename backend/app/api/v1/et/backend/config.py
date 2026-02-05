"""
Configuration management for SatyaSetu
Centralized settings with environment variable support
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    
    # CORS Settings
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # External Service APIs
    OPENAI_API_KEY: Optional[str] = None
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    ELEVENLABS_API_KEY: Optional[str] = None
    
    # Database & Cache
    REDIS_URL: str = "redis://localhost:6379"
    VECTOR_DB_INDEX: str = "satyasetu-rural-cybersecurity"
    
    # AI Model Settings
    DEFAULT_LANGUAGE: str = "hi"  # Hindi
    MAX_RESPONSE_LENGTH: int = 500
    PROCESSING_TIMEOUT: int = 30
    
    # Security
    RATE_LIMIT_PER_MINUTE: int = 60
    MAX_AUDIO_SIZE_MB: int = 10
    
    # Telemetry
    MAX_TELEMETRY_EVENTS: int = 1000
    TELEMETRY_RETENTION_HOURS: int = 24
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()