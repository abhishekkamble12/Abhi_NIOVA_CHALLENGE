"""AWS Configuration for EC2 in ap-south-1"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class AWSSettings(BaseSettings):
    # AWS Region
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-south-1")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    
    # Aurora PostgreSQL
    DB_HOST: str = os.getenv("DB_HOST", "")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "hiveminddb")
    
    # ElastiCache Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_SSL: bool = os.getenv("REDIS_SSL", "false").lower() == "true"
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    
    # S3
    S3_BUCKET: str = os.getenv("S3_BUCKET", "")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    
    # Bedrock
    BEDROCK_MODEL_EMBEDDING: str = os.getenv("BEDROCK_MODEL_EMBEDDING", "amazon.titan-embed-text-v2:0")
    BEDROCK_MODEL_TEXT: str = os.getenv("BEDROCK_MODEL_TEXT", "anthropic.claude-3-sonnet-20240229-v1:0")
    
    # EventBridge
    EVENT_BUS_NAME: str = os.getenv("EVENT_BUS_NAME", "default")
    
    # Cache TTL
    CACHE_TTL_EMBEDDING: int = int(os.getenv("CACHE_TTL_EMBEDDING", "86400"))
    CACHE_TTL_FEED: int = int(os.getenv("CACHE_TTL_FEED", "300"))

@lru_cache()
def get_aws_settings() -> AWSSettings:
    return AWSSettings()
