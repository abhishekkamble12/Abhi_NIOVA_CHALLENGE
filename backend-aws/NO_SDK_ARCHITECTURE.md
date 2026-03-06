# HiveMind AWS Backend - No AWS CLI/SDK Architecture

## 🎯 Zero Dependency Architecture

This backend operates **without AWS CLI and without AWS SDK (boto3/aioboto3)**.

All AWS services are accessed via:
- **Direct TCP connections** (Aurora, Redis)
- **HTTP APIs with SigV4 signing** (S3, Bedrock, EventBridge)
- **Environment variables** for configuration

---

## 📦 Dependencies

```
fastapi==0.109.0
uvicorn==0.27.0
asyncpg==0.29.0
redis==5.0.1
httpx==0.26.0
aws-requests-auth==0.4.3
python-dotenv==1.0.0
```

**NOT INCLUDED:**
- ❌ boto3
- ❌ aioboto3
- ❌ awscli
- ❌ botocore

---

## 🔧 Configuration

All configuration via `.env` file:

```bash
# Aurora PostgreSQL (Direct TCP)
AURORA_ENDPOINT=cluster.us-east-1.rds.amazonaws.com
AURORA_PORT=5432
DB_USERNAME=postgres
DB_PASSWORD=your_password
DB_NAME=hivemind

# ElastiCache Redis (Direct TCP)
REDIS_ENDPOINT=cache.us-east-1.cache.amazonaws.com
REDIS_PORT=6379
REDIS_SSL=true

# S3 (HTTP with SigV4)
S3_BUCKET=hivemind-media
S3_ENDPOINT=https://hivemind-media.s3.us-east-1.amazonaws.com
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# Bedrock (HTTP with SigV4)
BEDROCK_ENDPOINT=https://bedrock-runtime.us-east-1.amazonaws.com
BEDROCK_MODEL_EMBEDDING=amazon.titan-embed-text-v2:0
BEDROCK_MODEL_TEXT=anthropic.claude-3-sonnet-20240229-v1:0

# EventBridge (HTTP with SigV4)
EVENTBRIDGE_ENDPOINT=https://events.us-east-1.amazonaws.com
EVENT_BUS_NAME=hivemind-events
```

---

## 🚀 Quick Start

```powershell
# 1. Configure environment
cp .env.example .env
# Edit .env with your endpoints and credentials

# 2. Run startup script
.\start.ps1

# 3. Run application
python start.py
```

---

## 🏗️ Service Architecture

### Aurora PostgreSQL
**Connection**: Direct TCP via `asyncpg`
```python
from services.aurora_service import get_db_connection

async with get_db_connection() as conn:
    result = await conn.fetchval('SELECT 1')
```

### ElastiCache Redis
**Connection**: Direct TCP via `redis.asyncio`
```python
from services.cache_service import get_cache_service

cache = get_cache_service()
await cache.set('key', 'value', ttl=3600)
```

### S3
**Connection**: HTTP API with SigV4 signing
```python
from services.s3_service import get_s3_service

s3 = get_s3_service()
url = await s3.upload_file(data, 'path/file.txt')
```

### Bedrock
**Connection**: HTTP API with SigV4 signing
```python
from services.bedrock_service import get_bedrock_service

bedrock = get_bedrock_service()
embedding = await bedrock.generate_embedding('text')
text = await bedrock.generate_text('prompt')
```

### EventBridge
**Connection**: HTTP API with SigV4 signing
```python
from services.event_service import get_event_service

events = get_event_service()
await events.article_created(id, title, content, category)
```

---

## ✅ Benefits

1. **No AWS CLI Required**
   - No `aws configure`
   - No AWS CLI installation
   - Works on any system with Python

2. **No boto3 Required**
   - Smaller dependency footprint
   - Faster installation
   - No botocore version conflicts

3. **Direct Connections**
   - Lower latency (no SDK overhead)
   - Explicit control over requests
   - Easier debugging

4. **Environment-Based**
   - All config in `.env`
   - Easy to deploy anywhere
   - No AWS credential files needed

5. **Portable**
   - Works in Docker without AWS CLI
   - Works in restricted environments
   - Works with any Python 3.8+

---

## 🧪 Testing

```powershell
# Run all service tests
python start.py
```

Tests verify:
- ✅ Aurora PostgreSQL connection
- ✅ ElastiCache Redis connection
- ✅ S3 HTTP upload/download
- ✅ Bedrock embedding generation
- ✅ Bedrock text generation
- ✅ EventBridge event publishing

---

## 📊 Comparison

| Feature | With boto3 | Without boto3 |
|---------|-----------|---------------|
| Dependencies | 15+ packages | 7 packages |
| Install size | ~50MB | ~15MB |
| AWS CLI required | Yes | No |
| Credential files | Yes | No |
| Configuration | Multiple sources | Single .env |
| Debugging | SDK abstraction | Direct HTTP |
| Portability | AWS-specific | Universal |

---

## 🔐 Security

- Credentials stored in `.env` (never commit)
- SigV4 signing for all HTTP requests
- SSL/TLS for all connections
- No credential files on disk

---

## 🎯 Use Cases

Perfect for:
- Docker containers without AWS CLI
- Restricted environments
- Minimal dependency deployments
- Non-AWS cloud platforms
- Development environments
- CI/CD pipelines

---

## 📝 Summary

✅ **Zero AWS CLI dependency**  
✅ **Zero boto3 dependency**  
✅ **Direct HTTP/TCP connections**  
✅ **Environment variable configuration**  
✅ **Portable and lightweight**  
✅ **Production-ready**

Run with: `python start.py`
