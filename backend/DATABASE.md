# Database Infrastructure Documentation

## Overview

Production-grade async database layer using SQLAlchemy 2.0 with PostgreSQL and pgvector support.

## Architecture

```
backend/app/core/database.py
├── Async Engine (asyncpg/aiosqlite)
├── Session Factory (AsyncSessionLocal)
├── Base (Declarative Base)
├── get_db() (FastAPI Dependency)
├── init_pgvector() (Startup)
├── create_tables() (Startup)
└── close_db() (Shutdown)
```

## Key Features

✅ **SQLAlchemy 2.0 async style**  
✅ **PostgreSQL with asyncpg driver**  
✅ **SQLite with aiosqlite for development**  
✅ **pgvector extension support**  
✅ **Connection pooling with health checks**  
✅ **Automatic lifecycle management**  
✅ **SQL query logging in development**  
✅ **Alembic migration ready**  

## Configuration

### Database URL Format

```bash
# Development (SQLite)
DATABASE_URL=sqlite+aiosqlite:///./hivemind.db

# Production (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/hivemind
```

### Connection Pool Settings

```python
pool_size=5           # Number of connections to maintain
max_overflow=10       # Additional connections when pool exhausted
pool_pre_ping=True    # Verify connections before use
pool_recycle=3600     # Recycle connections after 1 hour
```

## Usage in Routes

### Basic CRUD Operations

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.example import Article

router = APIRouter()

@router.get("/articles/{article_id}")
async def get_article(article_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Article).filter(Article.id == article_id)
    )
    article = result.scalar_one_or_none()
    return article

@router.post("/articles")
async def create_article(title: str, content: str, db: AsyncSession = Depends(get_db)):
    article = Article(title=title, content=content)
    db.add(article)
    await db.commit()
    await db.refresh(article)
    return article

@router.put("/articles/{article_id}")
async def update_article(article_id: int, title: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Article).filter(Article.id == article_id)
    )
    article = result.scalar_one_or_none()
    if article:
        article.title = title
        await db.commit()
    return article

@router.delete("/articles/{article_id}")
async def delete_article(article_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Article).filter(Article.id == article_id)
    )
    article = result.scalar_one_or_none()
    if article:
        await db.delete(article)
        await db.commit()
    return {"deleted": True}
```

### Vector Search Operations

```python
from pgvector.sqlalchemy import Vector
from app.models.example import Article

@router.post("/articles/search")
async def search_similar_articles(
    query_embedding: list[float],
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Article)
        .order_by(Article.embedding.l2_distance(query_embedding))
        .limit(limit)
    )
    articles = result.scalars().all()
    return articles
```

## Creating Models

### Basic Model

```python
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### Model with Vector Embeddings

```python
from sqlalchemy import Column, Integer, String, Text
from pgvector.sqlalchemy import Vector
from app.core.database import Base
from app.core.config import settings

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    
    # Vector embedding (384 dimensions for all-MiniLM-L6-v2)
    embedding = Column(Vector(settings.VECTOR_DIMENSION))
```

## Alembic Migrations

### Setup

```bash
# Initialize Alembic
alembic init alembic

# Edit alembic.ini
sqlalchemy.url = postgresql+asyncpg://user:pass@localhost/hivemind
```

### Configure env.py

```python
# alembic/env.py
from app.core.database import Base
from app.core.config import settings
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

# Import all models
from app.models.example import Article, SocialPost, VideoSegment

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
target_metadata = Base.metadata

async def run_migrations_online():
    connectable = create_async_engine(settings.DATABASE_URL)
    
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    
    await connectable.dispose()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()
```

### Create Migration

```bash
# Auto-generate migration
alembic revision --autogenerate -m "Add articles table"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## pgvector Operations

### Distance Functions

```python
# L2 distance (Euclidean)
.order_by(Article.embedding.l2_distance(query_vector))

# Cosine distance
.order_by(Article.embedding.cosine_distance(query_vector))

# Inner product
.order_by(Article.embedding.max_inner_product(query_vector))
```

### Creating Indexes

```sql
-- IVFFlat index for approximate search
CREATE INDEX ON articles USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

-- HNSW index for better recall
CREATE INDEX ON articles USING hnsw (embedding vector_l2_ops);
```

## Lifecycle Management

### Startup Events

```python
# In main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_pgvector()    # Enable pgvector extension
    await create_tables()    # Create all tables
    yield
    # Shutdown
    await close_db()         # Close connections
```

### Manual Control

```python
from app.core.database import engine, Base

# Create tables manually
async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)

# Drop tables
async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.drop_all)
```

## Testing

### Test Database Setup

```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.database import Base

@pytest.fixture
async def test_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine) as session:
        yield session
    
    await engine.dispose()
```

## Troubleshooting

### Connection Issues

```python
# Check if database is accessible
from app.core.database import engine

async def check_connection():
    async with engine.connect() as conn:
        result = await conn.execute("SELECT 1")
        print("Database connected:", result.scalar())
```

### SQL Logging

```python
# Enable in development
ENVIRONMENT=development  # Automatically enables SQL echo
```

### Pool Exhaustion

```python
# Increase pool size in database.py
pool_size=10
max_overflow=20
```

## Security Best Practices

1. **Use connection pooling** - Prevents connection exhaustion
2. **Enable pool_pre_ping** - Detects stale connections
3. **Use parameterized queries** - SQLAlchemy handles this automatically
4. **Rotate credentials** - Update DATABASE_URL regularly
5. **Use SSL in production** - Add `?sslmode=require` to DATABASE_URL

## Performance Tips

1. **Use indexes** - Add indexes on frequently queried columns
2. **Batch operations** - Use bulk_insert_mappings for large inserts
3. **Lazy loading** - Use selectinload/joinedload for relationships
4. **Connection pooling** - Tune pool_size based on load
5. **Vector indexes** - Use IVFFlat or HNSW for large vector datasets

## Migration from Sync to Async

All legacy synchronous code is preserved as comments in database.py. To migrate existing code:

```python
# Old (sync)
def get_articles(db: Session):
    return db.query(Article).all()

# New (async)
async def get_articles(db: AsyncSession):
    result = await db.execute(select(Article))
    return result.scalars().all()
```
