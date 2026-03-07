# Database Integration Refactoring Guide

## Problem Statement

The current database integration uses **asyncpg** with async/await, which is incompatible with AWS Lambda's synchronous execution model.

### Before (asyncpg - NOT Lambda-compatible)
```python
import asyncpg

async def get_aurora_connection():
    return await asyncpg.connect(
        host=AURORA_HOST,
        database=AURORA_DB,
        user=AURORA_USER,
        password=AURORA_PASSWORD
    )

async def create_brand(brand_id: str, name: str, industry: str):
    conn = await get_aurora_connection()
    try:
        await conn.execute(
            'INSERT INTO brands (id, name, industry) VALUES ($1, $2, $3)',
            brand_id, name, industry
        )
    finally:
        await conn.close()
```

**Issues**:
- ❌ Requires async/await
- ❌ Not compatible with Lambda synchronous handlers
- ❌ Requires asyncio.run() wrapper
- ❌ Creates new connection every invocation

## Solution: psycopg2

### After (psycopg2 - Lambda-compatible)
```python
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=5
    )

@contextmanager
def db_connection():
    """Context manager for automatic connection cleanup"""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def create_brand(brand_id: str, name: str, industry: str):
    """Synchronous database operation"""
    with db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "INSERT INTO brands (id, name, industry, created_at) VALUES (%s, %s, %s, %s)",
            (brand_id, name, industry, datetime.utcnow())
        )
        return cursor.fetchone()
```

**Benefits**:
- ✅ Synchronous (no async/await)
- ✅ Lambda-compatible
- ✅ Automatic connection cleanup
- ✅ Returns dict results (RealDictCursor)
- ✅ Transaction management (commit/rollback)

## New Database Service API

### File: `services/database_service.py`

All functions are synchronous and Lambda-compatible.

### Brand Operations
```python
from services.database_service import create_brand, get_brand, list_brands

# Create
brand = create_brand('brand-123', 'TechCorp', 'technology')

# Get
brand = get_brand('brand-123')

# List
brands = list_brands(limit=100)
```

### Social Post Operations
```python
from services.database_service import create_post, get_post, get_brand_posts

# Create
post = create_post(
    post_id='post-123',
    brand_id='brand-123',
    platform='instagram',
    content='Post content...',
    media_url='s3://bucket/image.jpg'
)

# Get
post = get_post('post-123')

# Get brand posts
posts = get_brand_posts('brand-123', limit=50)
```

### Engagement Tracking
```python
from services.database_service import track_engagement, get_post_analytics

# Track
engagement = track_engagement(
    post_id='post-123',
    likes=150,
    comments=25,
    shares=10,
    clicks=500
)

# Get analytics
analytics = get_post_analytics('post-123')
```

### Video Operations
```python
from services.database_service import store_video_metadata, update_video_transcription, get_video

# Store
video = store_video_metadata(
    video_id='video-123',
    s3_url='s3://bucket/video.mp4',
    duration=120.5,
    transcription=None
)

# Update transcription
updated = update_video_transcription('video-123', 'Transcription text...')

# Get
video = get_video('video-123')
```

### Article Operations
```python
from services.database_service import create_article, get_articles_by_category

# Create
article = create_article(
    article_id='article-123',
    title='AI News',
    url='https://example.com/article',
    category='technology',
    published_date=datetime.utcnow()
)

# Get by category
articles = get_articles_by_category('technology', limit=20)
```

### User Preferences
```python
from services.database_service import get_user_preferences, upsert_user_preferences

# Get
prefs = get_user_preferences('user-123')

# Upsert
prefs = upsert_user_preferences(
    user_id='user-123',
    preferred_platforms=['instagram', 'linkedin'],
    preferred_categories=['tech', 'business'],
    notification_settings={'email': True, 'push': False}
)
```

## SQLAlchemy Support

### File: `services/database_sqlalchemy.py`

For projects using SQLAlchemy ORM models.

### Configuration
```python
from services.database_sqlalchemy import get_db_session, engine

# Engine with NullPool (no connection pooling for Lambda)
# Connection string from environment variables
```

### Usage with Models
```python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime
from services.database_sqlalchemy import get_db_session

Base = declarative_base()

class Brand(Base):
    __tablename__ = 'brands'
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    industry = Column(String(100))
    created_at = Column(DateTime)

# Lambda handler
def handler(event, context):
    with get_db_session() as session:
        # Query
        brand = session.query(Brand).filter_by(id='brand-123').first()
        
        # Create
        new_brand = Brand(id='brand-456', name='TechCorp', industry='tech')
        session.add(new_brand)
        
        # Update
        brand.name = 'Updated Name'
        
        # Delete
        session.delete(brand)
    
    return {'statusCode': 200}
```

### Raw SQL Queries
```python
from services.database_sqlalchemy import execute_raw_sql

result = execute_raw_sql(
    "SELECT * FROM brands WHERE industry = :industry",
    {"industry": "technology"}
)
```

## Lambda Handler Integration

### Before (asyncpg)
```python
import asyncio
from services.storage_service import get_brand, create_post

async def async_handler(event, context):
    brand = await get_brand(brand_id)  # ❌ Async
    await create_post(...)  # ❌ Async
    return {'statusCode': 200}

def handler(event, context):
    return asyncio.run(async_handler(event, context))
```

### After (psycopg2)
```python
from services.database_service import get_brand, create_post

def handler(event, context):
    brand = get_brand(brand_id)  # ✅ Synchronous
    create_post(...)  # ✅ Synchronous
    return {'statusCode': 200}
```

**No asyncio.run() needed!**

## Environment Variables

Required environment variables for Lambda:

```bash
DB_HOST=hivemind-cluster.cluster-xxx.ap-south-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=hiveminddb
DB_USER=hivemind
DB_PASSWORD=<secret>
```

### CloudFormation Configuration
```yaml
Environment:
  Variables:
    DB_HOST: !GetAtt AuroraCluster.Endpoint.Address
    DB_PORT: 5432
    DB_NAME: hiveminddb
    DB_USER: hivemind
    DB_PASSWORD: !Ref DBPassword
```

## Lambda Layer Setup

### Install Dependencies
```bash
cd lambda-microservices/layers

# Create python directory
mkdir -p python/lib/python3.11/site-packages

# Install psycopg2-binary
pip install -r requirements-db.txt -t python/lib/python3.11/site-packages

# Create layer zip
zip -r database-layer.zip python/
```

### CloudFormation Layer
```yaml
DatabaseLayer:
  Type: AWS::Lambda::LayerVersion
  Properties:
    LayerName: hivemind-database-layer
    Content:
      S3Bucket: my-lambda-layers
      S3Key: database-layer.zip
    CompatibleRuntimes:
      - python3.11
```

### Attach to Lambda
```yaml
MyFunction:
  Type: AWS::Lambda::Function
  Properties:
    Layers:
      - !Ref DatabaseLayer
```

## Connection Management

### Context Manager Pattern
```python
with db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM brands")
    results = cursor.fetchall()
# Connection automatically closed
```

### Manual Connection
```python
conn = get_db_connection()
try:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM brands")
    results = cursor.fetchall()
    conn.commit()
finally:
    conn.close()  # Must close manually
```

## Transaction Management

### Automatic (Context Manager)
```python
with db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("INSERT INTO brands ...")
    cursor.execute("INSERT INTO social_posts ...")
    # Automatically commits on success
    # Automatically rolls back on exception
```

### Manual
```python
conn = get_db_connection()
try:
    cursor = conn.cursor()
    cursor.execute("INSERT INTO brands ...")
    cursor.execute("INSERT INTO social_posts ...")
    conn.commit()
except Exception:
    conn.rollback()
    raise
finally:
    conn.close()
```

## Error Handling

```python
from psycopg2 import IntegrityError, OperationalError

def create_brand_safe(brand_id, name, industry):
    try:
        return create_brand(brand_id, name, industry)
    except IntegrityError:
        # Duplicate key
        return {'error': 'Brand already exists'}
    except OperationalError:
        # Connection error
        return {'error': 'Database connection failed'}
    except Exception as e:
        return {'error': str(e)}
```

## Performance Considerations

### No Connection Pooling
Lambda containers are ephemeral. Use **NullPool** (no pooling):
```python
engine = create_engine(DATABASE_URL, poolclass=NullPool)
```

### Connection Timeout
Set short timeout to fail fast:
```python
connect_args={'connect_timeout': 5}
```

### RDS Proxy (Recommended)
For high concurrency, use AWS RDS Proxy:
- Connection pooling
- Automatic failover
- IAM authentication

```yaml
RDSProxy:
  Type: AWS::RDS::DBProxy
  Properties:
    DBProxyName: hivemind-proxy
    EngineFamily: POSTGRESQL
    Auth:
      - AuthScheme: SECRETS
        SecretArn: !Ref DBSecret
    RoleArn: !GetAtt RDSProxyRole.Arn
    VpcSubnetIds: !Ref SubnetIds
```

## Migration Checklist

- [x] Replace asyncpg with psycopg2
- [x] Remove async/await from database functions
- [x] Add context manager for connection cleanup
- [x] Update Lambda handlers to use synchronous functions
- [x] Add psycopg2-binary to Lambda layer
- [x] Update environment variables
- [x] Test connection in Lambda
- [ ] Consider RDS Proxy for production
- [ ] Add connection retry logic
- [ ] Implement database health checks

## Testing

### Local Testing
```python
import os
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '5432'
os.environ['DB_NAME'] = 'hiveminddb'
os.environ['DB_USER'] = 'postgres'
os.environ['DB_PASSWORD'] = 'password'

from services.database_service import create_brand, get_brand

# Test
brand = create_brand('test-123', 'TestCorp', 'tech')
print(brand)

retrieved = get_brand('test-123')
print(retrieved)
```

### Lambda Testing
```bash
# Test deployed function
aws lambda invoke \
  --function-name hivemind-social-create-brand \
  --payload '{"body": "{\"name\":\"Test\",\"industry\":\"tech\"}"}' \
  response.json

cat response.json
```

## Summary

### Key Changes
- ✅ **asyncpg** → **psycopg2-binary**
- ✅ **async/await** → **synchronous functions**
- ✅ **Manual connection management** → **context managers**
- ✅ **Connection pooling** → **NullPool (no pooling)**
- ✅ **Complex async patterns** → **simple synchronous code**

### Benefits
- ✅ Lambda-compatible
- ✅ Simpler code (no async/await)
- ✅ Automatic connection cleanup
- ✅ Transaction management
- ✅ Better error handling
- ✅ Production-ready

All database operations are now **fully compatible with AWS Lambda**.
