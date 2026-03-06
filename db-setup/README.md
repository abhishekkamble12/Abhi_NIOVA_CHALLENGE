# Database Setup - AI Media OS

This folder contains all database setup scripts and documentation for AI Media OS, including vector database configuration.

## Files

### 1. `vector.md`
Complete guide for setting up vector database (pgvector) for semantic search and content similarity.

**Contents:**
- Why vector database is needed
- Comparison of vector DB options (pgvector, Pinecone, Weaviate, Qdrant)
- Installation instructions for pgvector
- Python integration with sentence-transformers
- Performance optimization tips
- Scaling strategy
- Cost analysis

**When to use:** Before implementing semantic search features

### 2. `schema_vector.sql`
SQL schema file to add vector support to existing PostgreSQL database.

**Contents:**
- Enable pgvector extension
- Add vector columns to existing tables (articles, generated_posts, video_scenes)
- Create new vector-specific tables (user_interest_embeddings, cross_module_links)
- Create IVFFlat indexes for fast similarity search
- Helper functions for vector operations
- Views for analytics

**When to use:** Run this after setting up base PostgreSQL database

## Quick Start

### Step 1: Install pgvector

```bash
# Using Docker (recommended for development)
docker run -d \
  --name postgres-vector \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=aimedios \
  -p 5432:5432 \
  ankane/pgvector
```

### Step 2: Run Schema Script

```bash
psql -U postgres -d aimedios -f schema_vector.sql
```

### Step 3: Install Python Dependencies

```bash
pip install pgvector sentence-transformers
```

### Step 4: Verify Setup

```sql
-- Check if pgvector is installed
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Check vector columns
SELECT table_name, column_name 
FROM information_schema.columns 
WHERE data_type = 'USER-DEFINED' AND udt_name = 'vector';
```

## Integration Points

### News Feed Module
- **Articles table**: Store article embeddings for semantic search
- **user_interest_embeddings table**: Aggregate user preferences as vectors
- **Use case**: Find similar articles, personalized recommendations

### Social Media Module
- **generated_posts table**: Store post embeddings for pattern matching
- **Use case**: Find similar high-performing posts, content inspiration

### Video Module
- **video_scenes table**: Store scene embeddings for similarity detection
- **Use case**: Find similar video segments, suggest editing patterns

### Cross-Module Intelligence
- **cross_module_links table**: Link related content across modules
- **Use case**: News article → social post → video content connections

## Performance Tuning

### For < 100K vectors
```sql
CREATE INDEX ON articles USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### For 100K - 1M vectors
```sql
CREATE INDEX ON articles USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 1000);
```

### Query Performance
```sql
-- Faster, less accurate
SET ivfflat.probes = 10;

-- Slower, more accurate
SET ivfflat.probes = 100;
```

## Migration Path

1. **MVP (< 10K vectors)**: Use pgvector with basic setup
2. **Growth (10K - 100K)**: Optimize pgvector indexes
3. **Scale (100K - 500K)**: Fine-tune pgvector, consider read replicas
4. **Enterprise (> 500K)**: Migrate to Pinecone or Qdrant

## Monitoring

### Check Embedding Coverage
```sql
SELECT * FROM articles_embedding_status;
```

### Check Index Usage
```sql
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE indexname LIKE '%embedding%';
```

### Check Storage Size
```sql
SELECT 
    pg_size_pretty(pg_total_relation_size('articles')) as total_size,
    pg_size_pretty(pg_indexes_size('articles')) as indexes_size;
```

## Troubleshooting

### Slow Queries
- Increase `ivfflat.probes`
- Rebuild index with more lists
- Check if index is being used (EXPLAIN ANALYZE)

### Out of Memory
- Reduce batch size in embedding generation
- Increase PostgreSQL shared_buffers

### Low Similarity Scores
- Check embedding model consistency
- Verify text preprocessing
- Ensure embeddings are normalized

## Next Steps

1. Read `vector.md` for detailed setup guide
2. Run `schema_vector.sql` to add vector support
3. Implement VectorService in backend
4. Migrate existing data to include embeddings
5. Update API endpoints to use vector search
6. Monitor performance and optimize

## References

- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [Sentence Transformers](https://www.sbert.net/)
- [Vector Database Comparison](https://benchmark.vectorview.ai/)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
