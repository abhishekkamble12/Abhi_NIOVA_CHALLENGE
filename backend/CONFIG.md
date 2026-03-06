# Configuration Guide

## Overview

HiveMind uses a centralized configuration system built with Pydantic BaseSettings for type-safe, validated environment configuration.

## Quick Start

1. **Copy the example file:**
   ```bash
   copy .env.example .env
   ```

2. **Edit `.env` with your values:**
   ```bash
   notepad .env
   ```

3. **Use in code:**
   ```python
   from app.core.config import settings
   
   print(settings.DATABASE_URL)
   print(settings.OPENAI_API_KEY)
   ```

## Environment Modes

### Development (default)
- SQLite database
- Debug mode enabled
- Verbose logging
- CORS allows all origins

### Staging
- PostgreSQL with pgvector
- Debug mode disabled
- Moderate logging
- Restricted CORS

### Production
- PostgreSQL with pgvector
- Debug mode disabled
- Error-level logging only
- Strict CORS
- AWS S3 for storage

## Configuration Variables

### Core Settings
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENVIRONMENT` | No | `development` | Environment mode |
| `DEBUG` | No | `True` | Debug mode flag |
| `PROJECT_NAME` | No | `AI Media OS - HiveMind` | Project name |
| `API_V1_PREFIX` | No | `/api/v1` | API route prefix |
| `LOG_LEVEL` | No | `info` | Logging level |

### Database
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | No | `sqlite:///./hivemind.db` | Database connection string |
| `REDIS_URL` | No | `redis://localhost:6379/0` | Redis connection string |

### AI Services
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | No | `None` | OpenAI API key |
| `NEWS_API_KEY` | No | `None` | NewsAPI key |

### Vector Database
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VECTOR_DIMENSION` | No | `384` | Embedding vector size |
| `EMBEDDING_MODEL` | No | `all-MiniLM-L6-v2` | Sentence transformer model |

### Storage
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `UPLOAD_DIR` | No | `uploads` | Local upload directory |

### AWS (Production)
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AWS_ACCESS_KEY_ID` | No | `None` | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | No | `None` | AWS secret key |
| `AWS_REGION` | No | `us-east-1` | AWS region |
| `S3_BUCKET` | No | `None` | S3 bucket name |

## Helper Methods

```python
from app.core.config import settings

# Check environment
if settings.is_production():
    # Production-specific logic
    pass

if settings.is_development():
    # Development-specific logic
    pass

if settings.is_staging():
    # Staging-specific logic
    pass
```

## Validation

The configuration system automatically validates:
- ✅ Environment must be: `development`, `staging`, or `production`
- ✅ Log level must be: `debug`, `info`, `warning`, `error`, or `critical`
- ✅ Upload directories are created automatically

## Security Best Practices

1. **Never commit `.env` to version control**
   - Already in `.gitignore`

2. **Use different keys per environment**
   - Development: Test API keys
   - Production: Production API keys

3. **Rotate secrets regularly**
   - Update API keys quarterly
   - Use AWS Secrets Manager in production

4. **Restrict CORS in production**
   - Remove `"*"` from `ALLOWED_ORIGINS`
   - Add only your production domains

## Migration Path

### Local → Staging
```bash
# Update .env
ENVIRONMENT=staging
DATABASE_URL=postgresql://user:pass@staging-db:5432/hivemind
DEBUG=False
```

### Staging → Production
```bash
# Update .env
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@prod-db:5432/hivemind
DEBUG=False
LOG_LEVEL=error
AWS_ACCESS_KEY_ID=prod-key
S3_BUCKET=hivemind-prod-storage
```

## Troubleshooting

### Configuration not loading
- Ensure `.env` file exists in `backend/` directory
- Check file permissions
- Verify no syntax errors in `.env`

### Validation errors
- Check `ENVIRONMENT` value is valid
- Verify `LOG_LEVEL` is lowercase
- Ensure required fields are set

### Import errors
```python
# ✅ Correct
from app.core.config import settings

# ❌ Wrong
from core.config import settings
```
