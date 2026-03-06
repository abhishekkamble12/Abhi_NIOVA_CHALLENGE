from pydantic_settings import BaseSettings
from typing import List, Optional
from pydantic import field_validator
import os

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PROJECT_NAME: str = "AI Media OS - HiveMind"
    API_V1_PREFIX: str = "/api/v1"
    LOG_LEVEL: str = "info"
    
    # CORS - Preserved from original
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "*"  # Allow all for local development
    ]
    
    # Database
    DATABASE_URL: str = "sqlite:///./hivemind.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None
    
    # Vector Database
    VECTOR_DIMENSION: int = 384
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Storage
    UPLOAD_DIR: str = "uploads"
    
    # AWS (Optional for production)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: Optional[str] = None
    
    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)
    
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = ["debug", "info", "warning", "error", "critical"]
        if v.lower() not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v.lower()
    
    @field_validator("UPLOAD_DIR")
    @classmethod
    def create_upload_dir(cls, v: str) -> str:
        os.makedirs(v, exist_ok=True)
        os.makedirs(os.path.join(v, "videos"), exist_ok=True)
        os.makedirs(os.path.join(v, "images"), exist_ok=True)
        return v
    
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"
    
    def is_staging(self) -> bool:
        return self.ENVIRONMENT == "staging"
    
    model_config = {
        "env_file": ".env",
        "extra": "ignore",
        "case_sensitive": True
    }

settings = Settings()
