# Configuration Quick Reference

## Import & Usage

```python
from app.core.config import settings

# Access any setting
database_url = settings.DATABASE_URL
api_key = settings.OPENAI_API_KEY
vector_dim = settings.VECTOR_DIMENSION

# Environment checks
if settings.is_production():
    # Use S3 storage
    pass
elif settings.is_development():
    # Use local storage
    pass
```

## All Available Settings

```python
# Core
settings.ENVIRONMENT          # "development" | "staging" | "production"
settings.DEBUG                # bool
settings.PROJECT_NAME         # str
settings.API_V1_PREFIX        # str (default: "/api/v1")
settings.LOG_LEVEL            # str (default: "info")

# CORS
settings.ALLOWED_ORIGINS      # List[str]

# Database
settings.DATABASE_URL         # str
settings.REDIS_URL            # str

# AI Services
settings.OPENAI_API_KEY       # Optional[str]
settings.NEWS_API_KEY         # Optional[str]

# Vector DB
settings.VECTOR_DIMENSION     # int (default: 384)
settings.EMBEDDING_MODEL      # str (default: "all-MiniLM-L6-v2")

# Storage
settings.UPLOAD_DIR           # str (default: "uploads")

# AWS
settings.AWS_ACCESS_KEY_ID    # Optional[str]
settings.AWS_SECRET_ACCESS_KEY # Optional[str]
settings.AWS_REGION           # str (default: "us-east-1")
settings.S3_BUCKET            # Optional[str]
```

## Helper Methods

```python
settings.is_production()      # bool
settings.is_development()     # bool
settings.is_staging()         # bool
```

## Setup

1. Copy `.env.example` to `.env`
2. Fill in your values
3. Import and use `settings` anywhere in your code

## Files

- `app/core/config.py` - Configuration class
- `.env` - Your local config (gitignored)
- `.env.example` - Template with all variables
- `CONFIG.md` - Full documentation
