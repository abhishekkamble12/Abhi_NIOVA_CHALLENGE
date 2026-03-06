# Vector Database Setup Guide

## Overview

AI Media OS uses **vector embeddings** for semantic search and content similarity across all modules. This enables intelligent content recommendations, cross-module learning, and personalized user experiences.

## Why Vector Database?

### Use Cases in AI Media OS

1. **News Feed Personalization**
   - Store article embeddings (384-dim vectors)
   - Find similar articles using cosine similarity
   - Match user interests with content semantically

2. **Social Media Content Intelligence**
   - Store successful post embeddings
   - Find similar high-performing content patterns
   - Generate content based on semantic similarity to top posts

3. **Video Content Analysis**
   - Store video scene embeddings
   - Find similar video segments across library
   - Suggest editing patterns based on successful videos

4. **Cross-Module Intelligence**
   - Link related content across modules (news → social → video)
   - Build unified user interest profiles
   - Enable semantic search across all content types

## Vector Database Options

### Option 1: pgvector (PostgreSQL Extension) ✅ RECOMMENDED

**Pros:**
- Integrates with existing PostgreSQL database
- No additional infrastructure needed
- ACID compliance
- Supports hybrid queries (vector + relational)
- Free and open-source

**Cons:**
- Slower than specialized vector DBs at massive scale
- Limited to ~1M vectors efficiently

**Best for:** MVP and early-stage (< 1M vectors)

### Option 2: Pinecone

**Pros:**
- Managed service (no ops)
- Extremely fast at scale
- Built-in metadata filtering

**Cons:**
- Paid service ($70+/month)
- Vendor lock-in
- External dependency

**Best for:** Production scale (> 1M vectors)

### Option 3: Weaviate

**Pros:**
- Open-source
- GraphQL API
- Built-in ML models

**Cons:**
- Additional infrastructure
- More complex setup

**Best for:** Advanced ML pipelines

### Option 4: Qdrant

**Pros:**
- Open-source
- Rust-based (fast)
- Good Python SDK

**Cons:**
- Newer ecosystem
- Requires separate deployment

**Best for:** High-performance requirements

## Recommended Setup: pgvector

### Installation

#### 1. Install pgvector Extension

```bash
# Ubuntu/Debian
sudo apt-get install postgresql-14-pgvector

# macOS (Homebrew)
brew install pgvector

# Docker (recommended for development)
docker run -d \
  --name postgres-vector \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=aimedios \
  -p 5432:5432 \
  ankane/pgvector
```

#### 2. Enable Extension in Database

```sql
-- Connect to your database
psql -U postgres -d aimedios

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### Database Schema Updates

#### Add Vector Columns to Existing Tables

```sql
-- Articles table: Add embedding column
ALTER TABLE articles 
ADD COLUMN embedding vector(384);

-- Create index for fast similarity search
CREATE INDEX ON articles 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Generated posts table: Add embedding column
ALTER TABLE generated_posts 
ADD COLUMN embedding vector(384);

CREATE INDEX ON generated_posts 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Video scenes table: Add embedding column
ALTER TABLE video_scenes 
ADD COLUMN embedding vector(384);

CREATE INDEX ON video_scenes 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- User interest profiles: Store aggregated embeddings
CREATE TABLE user_interest_embeddings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    embedding vector(384) NOT NULL,
    interest_category VARCHAR(100),
    weight FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON user_interest_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 50);
```

### Python Integration

#### 1. Install Dependencies

```bash
pip install pgvector sentence-transformers
```

#### 2. Create Vector Service

Create `backend/app/services/vector_service.py`:

```python
from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from typing import List, Tuple
import numpy as np

class VectorService:
    def __init__(self):
        # Use lightweight model for embeddings
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector from text."""
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts efficiently."""
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
    
    async def find_similar_articles(
        self, 
        db, 
        query_embedding: List[float], 
        limit: int = 10,
        min_similarity: float = 0.7
    ) -> List[Tuple[int, float]]:
        """Find similar articles using cosine similarity."""
        
        query = text("""
            SELECT id, 1 - (embedding <=> :query_embedding) as similarity
            FROM articles
            WHERE embedding IS NOT NULL
            AND 1 - (embedding <=> :query_embedding) > :min_similarity
            ORDER BY embedding <=> :query_embedding
            LIMIT :limit
        """)
        
        result = await db.execute(
            query,
            {
                "query_embedding": str(query_embedding),
                "min_similarity": min_similarity,
                "limit": limit
            }
        )
        
        return [(row.id, row.similarity) for row in result]
    
    async def find_similar_posts(
        self,
        db,
        query_embedding: List[float],
        limit: int = 5
    ) -> List[Tuple[int, float]]:
        """Find similar social media posts."""
        
        query = text("""
            SELECT id, caption, 1 - (embedding <=> :query_embedding) as similarity
            FROM generated_posts
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> :query_embedding
            LIMIT :limit
        """)
        
        result = await db.execute(
            query,
            {"query_embedding": str(query_embedding), "limit": limit}
        )
        
        return [(row.id, row.similarity) for row in result]
    
    async def update_user_interest_profile(
        self,
        db,
        user_id: int,
        article_embeddings: List[List[float]],
        weights: List[float] = None
    ):
        """Update user interest profile with weighted average of article embeddings."""
        
        if not weights:
            weights = [1.0] * len(article_embeddings)
        
        # Calculate weighted average embedding
        weighted_sum = np.zeros(384)
        total_weight = sum(weights)
        
        for embedding, weight in zip(article_embeddings, weights):
            weighted_sum += np.array(embedding) * weight
        
        avg_embedding = (weighted_sum / total_weight).tolist()
        
        # Store or update user interest embedding
        query = text("""
            INSERT INTO user_interest_embeddings (user_id, embedding, interest_category, weight)
            VALUES (:user_id, :embedding, 'general', :weight)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                embedding = :embedding,
                weight = :weight,
                updated_at = CURRENT_TIMESTAMP
        """)
        
        await db.execute(
            query,
            {
                "user_id": user_id,
                "embedding": str(avg_embedding),
                "weight": total_weight
            }
        )
        await db.commit()
```

#### 3. Update News Feed Service

Modify `backend/app/services/news_service.py`:

```python
from app.services.vector_service import VectorService

class NewsService:
    def __init__(self):
        self.vector_service = VectorService()
    
    async def get_personalized_feed_with_vectors(
        self,
        db,
        user_id: int,
        limit: int = 20
    ):
        """Get personalized feed using vector similarity."""
        
        # Get user's interest embedding
        user_embedding_query = text("""
            SELECT embedding 
            FROM user_interest_embeddings 
            WHERE user_id = :user_id
            ORDER BY updated_at DESC
            LIMIT 1
        """)
        
        result = await db.execute(user_embedding_query, {"user_id": user_id})
        user_embedding = result.scalar()
        
        if not user_embedding:
            # Fallback to trending if no profile
            return await self.get_trending_articles(db, limit)
        
        # Find similar articles
        similar_articles = await self.vector_service.find_similar_articles(
            db,
            user_embedding,
            limit=limit,
            min_similarity=0.6
        )
        
        return similar_articles
```

### Migration Script

Create `backend/db-setup/migrate_to_vector.py`:

```python
import asyncio
from sqlalchemy import create_engine, text
from app.services.vector_service import VectorService
from app.core.config import settings

async def migrate_existing_data():
    """Migrate existing articles to include embeddings."""
    
    engine = create_engine(settings.DATABASE_URL)
    vector_service = VectorService()
    
    with engine.connect() as conn:
        # Get all articles without embeddings
        articles = conn.execute(text("""
            SELECT id, title, body 
            FROM articles 
            WHERE embedding IS NULL
            LIMIT 1000
        """)).fetchall()
        
        print(f"Found {len(articles)} articles to process")
        
        # Process in batches
        batch_size = 50
        for i in range(0, len(articles), batch_size):
            batch = articles[i:i+batch_size]
            
            # Generate embeddings
            texts = [f"{a.title} {a.body[:500]}" for a in batch]
            embeddings = vector_service.generate_batch_embeddings(texts)
            
            # Update database
            for article, embedding in zip(batch, embeddings):
                conn.execute(
                    text("""
                        UPDATE articles 
                        SET embedding = :embedding 
                        WHERE id = :id
                    """),
                    {"id": article.id, "embedding": str(embedding)}
                )
            
            conn.commit()
            print(f"Processed {i+len(batch)}/{len(articles)} articles")

if __name__ == "__main__":
    asyncio.run(migrate_existing_data())
```

## Performance Optimization

### Index Tuning

```sql
-- For datasets < 100K vectors
CREATE INDEX ON articles USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- For datasets 100K - 1M vectors
CREATE INDEX ON articles USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 1000);

-- For datasets > 1M vectors (consider Pinecone)
CREATE INDEX ON articles USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 10000);
```

### Query Optimization

```sql
-- Use approximate search for speed
SET ivfflat.probes = 10;  -- Check 10 lists (faster, less accurate)

-- Use exact search for accuracy
SET ivfflat.probes = 100;  -- Check 100 lists (slower, more accurate)
```

## Monitoring

### Check Index Usage

```sql
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE indexname LIKE '%embedding%';
```

### Check Vector Storage Size

```sql
SELECT 
    pg_size_pretty(pg_total_relation_size('articles')) as total_size,
    pg_size_pretty(pg_relation_size('articles')) as table_size,
    pg_size_pretty(pg_indexes_size('articles')) as indexes_size;
```

## Scaling Strategy

### Phase 1: MVP (< 10K vectors)
- Use pgvector with basic indexing
- Single PostgreSQL instance
- Acceptable: 50-100ms query time

### Phase 2: Growth (10K - 100K vectors)
- Optimize pgvector indexes (lists = 1000)
- Add read replicas for queries
- Target: 20-50ms query time

### Phase 3: Scale (100K - 1M vectors)
- Consider pgvector with optimized hardware
- OR migrate to Pinecone/Qdrant
- Target: < 20ms query time

### Phase 4: Enterprise (> 1M vectors)
- Migrate to Pinecone or Qdrant
- Distributed vector search
- Target: < 10ms query time

## Cost Analysis

| Solution | Setup Cost | Monthly Cost (100K vectors) | Monthly Cost (1M vectors) |
|----------|------------|----------------------------|---------------------------|
| pgvector | $0 | $0 (included in DB) | $0 (included in DB) |
| Pinecone | $0 | $70 | $200+ |
| Weaviate | $0 | $50 (hosting) | $200 (hosting) |
| Qdrant | $0 | $50 (hosting) | $200 (hosting) |

**Recommendation:** Start with pgvector, migrate to Pinecone at 500K+ vectors.

## Testing

### Test Vector Search

```python
# Test similarity search
async def test_vector_search():
    vector_service = VectorService()
    
    # Generate test embedding
    query = "artificial intelligence and machine learning"
    query_embedding = vector_service.generate_embedding(query)
    
    # Find similar articles
    similar = await vector_service.find_similar_articles(
        db,
        query_embedding,
        limit=5
    )
    
    print(f"Found {len(similar)} similar articles")
    for article_id, similarity in similar:
        print(f"Article {article_id}: {similarity:.3f} similarity")
```

## Troubleshooting

### Issue: Slow queries
**Solution:** Increase `ivfflat.probes` or rebuild index with more lists

### Issue: Out of memory
**Solution:** Reduce batch size in embedding generation

### Issue: Low similarity scores
**Solution:** Check embedding model, ensure text preprocessing is consistent

## Next Steps

1. Run migration script to add embeddings to existing data
2. Update API endpoints to use vector search
3. Monitor query performance
4. Optimize index parameters based on usage
5. Plan migration to Pinecone if scaling beyond 500K vectors

## References

- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [Sentence Transformers](https://www.sbert.net/)
- [Vector Database Comparison](https://benchmark.vectorview.ai/)
