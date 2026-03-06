# 🔍 Backend AWS Refactoring Analysis for HiveMind

## Executive Summary

This document analyzes the current FastAPI backend and provides a comprehensive breakdown of components for AWS migration. The analysis classifies each component by AWS service suitability (Lambda vs ECS/EC2) and identifies refactoring requirements.

---

## 📊 1. API Endpoints Inventory

### 1.1 Brand Management Endpoints

| Endpoint | Method | Handler | Database | AI/Vector | AWS Service |
|----------|--------|---------|----------|-----------|-------------|
| `/api/v1/brands` | POST | `create_brand` | ✅ Write | ✅ Embedding | Lambda |
| `/api/v1/brands/{id}` | GET | `get_brand` | ✅ Read | ❌ | Lambda |
| `/api/v1/brands` | GET | `list_brands` | ✅ Read | ❌ | Lambda |
| `/api/v1/brands/{id}` | PUT | `update_brand` | ✅ Write | ✅ Embedding | Lambda |
| `/api/v1/brands/{id}` | DELETE | `delete_brand` | ✅ Write | ❌ | Lambda |

**Characteristics:**
- Lightweight CRUD operations
- Embedding generation on create/update
- Suitable for Lambda (< 30s execution)

### 1.2 Article Management Endpoints

| Endpoint | Method | Handler | Database | AI/Vector | AWS Service |
|----------|--------|---------|----------|-----------|-------------|
| `/api/v1/articles` | POST | `create_article` | ✅ Write | ✅ Embedding | Lambda |
| `/api/v1/articles/{id}` | GET | `get_article` | ✅ Read | ❌ | Lambda |
| `/api/v1/articles` | GET | `list_articles` | ✅ Read | ❌ | Lambda |
| `/api/v1/articles/search/semantic` | GET | `search_articles` | ✅ Read | ✅ Vector Search | Lambda |
| `/api/v1/articles/{id}` | PUT | `update_article` | ✅ Write | ✅ Embedding | Lambda |
| `/api/v1/articles/{id}` | DELETE | `delete_article` | ✅ Write | ❌ | Lambda |

**Characteristics:**
- CRUD + semantic search
- Vector similarity queries
- Suitable for Lambda

### 1.3 Health & Root Endpoints

| Endpoint | Method | Handler | Database | AI/Vector | AWS Service |
|----------|--------|---------|----------|-----------|-------------|
| `/` | GET | `root` | ❌ | ❌ | Lambda |
| `/health` | GET | `health_check` | ❌ | ❌ | Lambda |

---

## 🤖 2. AI Processing Functions

### 2.1 Vector Embedding Generation

**File:** `app/services/vector_service.py`

**Class:** `VectorService`

**Functions:**
```python
generate_embedding(text: str) -> List[float]
  - Uses: SentenceTransformers (all-MiniLM-L6-v2)
  - Model Size: ~90MB
  - Execution Time: 50-200ms per text
  - Memory: ~500MB
  - AWS Service: Lambda (with model in /tmp or EFS)
  - Alternative: Bedrock Titan Embeddings

generate_batch_embeddings(texts: List[str]) -> List[List[float]]
  - Batch processing for efficiency
  - Execution Time: 2-10s for 100 texts
  - AWS Service: Lambda (< 15min timeout) or ECS for large batches
```

**Model Loading:**
- Lazy loading pattern (loads on first use)
- Model cached in memory
- **AWS Consideration:** Use Lambda layers or EFS for model storage

### 2.2 Vector Search Functions

**File:** `app/services/vector_service.py`

**Functions:**
```python
search_similar_articles(db, query_text, limit, min_similarity)
  - Generates query embedding
  - Executes pgvector cosine similarity search
  - Returns ranked results
  - Execution Time: 100-500ms
  - AWS Service: Lambda

search_similar_posts(db, query_text, platform, limit, min_similarity)
  - Platform-filtered vector search
  - AWS Service: Lambda

search_similar_video_scenes(db, query_text, video_id, limit, min_similarity)
  - Video scene semantic search
  - AWS Service: Lambda

find_similar_by_embedding(db, embedding, model_class, limit, min_similarity)
  - Generic vector search
  - AWS Service: Lambda
```

**Database Dependency:**
- All functions require PostgreSQL with pgvector
- **AWS Service:** Aurora PostgreSQL or RDS PostgreSQL with pgvector

---

## 💾 3. Database Operations

### 3.1 Database Configuration

**File:** `app/core/database.py`

**Components:**
```python
engine: AsyncEngine
  - SQLAlchemy async engine
  - Connection pooling (pool_size=5, max_overflow=10)
  - AWS Service: Aurora PostgreSQL Serverless v2

AsyncSessionLocal: async_sessionmaker
  - Session factory
  - Auto-commit disabled
  - AWS Service: Compatible with Aurora

get_db() -> AsyncSession
  - Dependency injection for FastAPI
  - AWS Service: Lambda compatible

init_pgvector()
  - Initializes pgvector extension
  - AWS Service: Run once on Aurora setup

create_tables()
  - Creates all tables
  - AWS Service: Run via Lambda or migration script
```

### 3.2 Database Models

**File:** `app/models/`

**Models with Vector Embeddings:**
1. `Brand` - 384-dim embedding
2. `Article` - 384-dim embedding
3. `GeneratedPost` - 384-dim embedding
4. `Video` - 384-dim embedding
5. `VideoScene` - 384-dim embedding
6. `UserPreferences` - 384-dim embedding

**Models without Embeddings:**
1. `User`
2. `Caption`
3. `UserBehavior`

**AWS Considerations:**
- All models compatible with Aurora PostgreSQL
- pgvector extension required
- Consider DynamoDB for high-throughput metadata

### 3.3 Service Layer Database Operations

**Brand Service:**
```python
create_brand() - INSERT + embedding generation
get_brand() - SELECT by ID
list_brands() - SELECT with pagination
update_brand() - UPDATE + re-generate embedding
delete_brand() - DELETE
```

**Article Service:**
```python
create_article() - INSERT + embedding generation
get_article() - SELECT by ID
list_articles() - SELECT with filters + pagination
search_articles() - Vector similarity search
update_article() - UPDATE + re-generate embedding
delete_article() - DELETE
increment_views() - UPDATE counter
```

**All operations are async and Lambda-compatible.**

---

## 🔄 4. Background Jobs & Async Tasks

### 4.1 Current Background Tasks

**None explicitly defined in codebase.**

**Potential Background Jobs:**
1. **Batch Embedding Generation**
   - Process: Generate embeddings for bulk imports
   - Trigger: S3 upload or SQS message
   - AWS Service: Lambda (< 1000 items) or ECS (> 1000 items)

2. **Vector Index Optimization**
   - Process: Rebuild pgvector indices
   - Trigger: Scheduled (weekly)
   - AWS Service: ECS Fargate task

3. **Analytics Aggregation**
   - Process: Compute engagement metrics
   - Trigger: EventBridge schedule
   - AWS Service: Lambda

4. **Cache Warming**
   - Process: Pre-populate Redis cache
   - Trigger: EventBridge schedule
   - AWS Service: Lambda

### 4.2 Async Processing Patterns

**Current Pattern:**
- Synchronous API responses
- Embedding generation blocks request

**AWS Pattern:**
- API Gateway → Lambda (accept request)
- SQS → Lambda (process embedding)
- EventBridge → Step Functions (orchestrate)

---

## 🔴 5. Redis Cache Usage

### 5.1 Cache Functions

**File:** `app/core/redis.py`

**Core Functions:**
```python
init_redis() - Initialize connection pool
close_redis() - Close connections
set_cache(key, value, ttl) - Set with TTL
get_cache(key) - Get with JSON deserialization
delete_cache(key) - Delete single key
delete_pattern(pattern) - Delete by pattern
```

**Specialized Functions:**
```python
cache_feed(user_id, feed_data, ttl=300)
  - Cache personalized news feeds
  - TTL: 5 minutes
  - AWS Service: ElastiCache Redis

get_cached_feed(user_id)
  - Retrieve cached feed
  - AWS Service: ElastiCache Redis

cache_ai_response(prompt_hash, response, ttl=3600)
  - Cache AI API responses
  - TTL: 1 hour
  - AWS Service: ElastiCache Redis

get_cached_ai_response(prompt_hash)
  - Retrieve cached AI response
  - AWS Service: ElastiCache Redis

cache_embeddings(content_id, embeddings, ttl=86400)
  - Cache vector embeddings
  - TTL: 24 hours
  - AWS Service: ElastiCache Redis

get_cached_embeddings(content_id)
  - Retrieve cached embeddings
  - AWS Service: ElastiCache Redis

check_rate_limit(user_id, action, limit, window)
  - Rate limiting with sliding window
  - AWS Service: ElastiCache Redis or API Gateway throttling
```

**AWS Migration:**
- Replace with ElastiCache Redis cluster
- Lambda functions connect via VPC
- Use Redis Cluster mode for high availability

---

## ⚡ 6. Components Suitable for AWS Lambda

### 6.1 API Handlers (All Endpoints)

**Characteristics:**
- Execution time: < 5 seconds
- Memory: 512MB - 1024MB
- Stateless operations
- Database connections via RDS Proxy

**Lambda Functions:**
```
lambda-brand-create
lambda-brand-get
lambda-brand-list
lambda-brand-update
lambda-brand-delete

lambda-article-create
lambda-article-get
lambda-article-list
lambda-article-search
lambda-article-update
lambda-article-delete

lambda-health-check
```

### 6.2 Lightweight AI Operations

**Functions:**
```
lambda-generate-embedding
  - Single text embedding
  - Execution: < 1s
  - Memory: 1024MB
  - Model: Load from EFS or Lambda layer

lambda-vector-search
  - Semantic search queries
  - Execution: < 2s
  - Memory: 512MB
```

### 6.3 Cache Operations

**Functions:**
```
lambda-cache-warm
  - Pre-populate cache
  - Execution: < 30s
  - Trigger: EventBridge schedule

lambda-cache-invalidate
  - Clear cache patterns
  - Execution: < 5s
  - Trigger: EventBridge event
```

---

## 🐳 7. Components Requiring ECS/EC2

### 7.1 Heavy Compute Operations

**Batch Embedding Generation:**
```
Task: Generate embeddings for 10,000+ items
Execution Time: 10-60 minutes
Memory: 2-4GB
AWS Service: ECS Fargate
Trigger: S3 upload or SQS batch
```

**Model Training/Fine-tuning:**
```
Task: Fine-tune embedding models
Execution Time: Hours
Memory: 8-16GB
GPU: Optional
AWS Service: EC2 with GPU or SageMaker
```

**Video Processing:**
```
Task: Video scene detection, transcription
Execution Time: 5-30 minutes per video
Memory: 4-8GB
AWS Service: ECS Fargate or MediaConvert
```

### 7.2 Long-Running Services

**WebSocket Server:**
```
File: app/core/websocket.py
Purpose: Real-time updates
AWS Service: ECS Fargate with ALB
Alternative: API Gateway WebSocket API
```

**Background Job Processor:**
```
Purpose: Process SQS messages
Execution: Continuous
AWS Service: ECS Fargate
Alternative: Lambda with SQS trigger (if < 15min)
```

---

## 🔗 8. Database Interaction Summary

### 8.1 Read Operations (Lambda-Compatible)

```
Brand:
  - get_brand(id) - Single SELECT
  - list_brands(user_id, pagination) - SELECT with LIMIT/OFFSET

Article:
  - get_article(id) - Single SELECT
  - list_articles(category, pagination) - SELECT with filters
  - search_articles(query) - Vector similarity SELECT

All read operations: < 500ms
```

### 8.2 Write Operations (Lambda-Compatible)

```
Brand:
  - create_brand() - INSERT + embedding generation (< 2s)
  - update_brand() - UPDATE + embedding generation (< 2s)
  - delete_brand() - DELETE (< 100ms)

Article:
  - create_article() - INSERT + embedding generation (< 2s)
  - update_article() - UPDATE + embedding generation (< 2s)
  - delete_article() - DELETE (< 100ms)
  - increment_views() - UPDATE counter (< 50ms)

All write operations: < 3s
```

### 8.3 Vector Search Operations (Lambda-Compatible)

```
search_similar_articles(query, limit=10)
  - Generate query embedding: 100-200ms
  - pgvector cosine similarity: 50-300ms
  - Total: < 500ms

search_similar_posts(query, platform, limit=10)
  - Similar performance profile
  - Total: < 500ms

search_similar_video_scenes(query, video_id, limit=10)
  - Similar performance profile
  - Total: < 500ms
```

**Database Requirements:**
- Aurora PostgreSQL with pgvector extension
- Connection pooling via RDS Proxy
- VPC configuration for Lambda access

---

## 📋 9. AWS Migration Strategy

### 9.1 Phase 1: Infrastructure Setup

```yaml
Services to Deploy:
  - VPC with public/private subnets
  - Aurora PostgreSQL Serverless v2 with pgvector
  - ElastiCache Redis cluster
  - RDS Proxy for connection pooling
  - S3 buckets for media storage
  - Secrets Manager for credentials
```

### 9.2 Phase 2: Lambda Functions

```yaml
API Handlers:
  - Convert each endpoint to Lambda function
  - Use Lambda layers for shared dependencies
  - Store SentenceTransformers model in EFS or S3
  - Connect to Aurora via RDS Proxy

Deployment:
  - Use AWS SAM or CDK
  - API Gateway for routing
  - Cognito for authentication
```

### 9.3 Phase 3: Replace AI Components

```yaml
Current: SentenceTransformers (self-hosted)
AWS Alternative: Amazon Bedrock Titan Embeddings

Benefits:
  - No model management
  - Auto-scaling
  - Pay-per-use
  - Faster cold starts

Migration:
  - Replace generate_embedding() with Bedrock API call
  - Update vector dimension if needed (1536 vs 384)
  - Migrate existing embeddings or regenerate
```

### 9.4 Phase 4: Background Jobs

```yaml
Batch Processing:
  - SQS queues for job distribution
  - Lambda for small batches (< 1000 items)
  - ECS Fargate for large batches (> 1000 items)
  - Step Functions for orchestration

Scheduled Tasks:
  - EventBridge rules for cron jobs
  - Lambda for cache warming
  - ECS for index optimization
```

---

## 🎯 10. Component Classification Summary

### Lambda-Suitable Components (90%)

```
✅ All API endpoints (12 endpoints)
✅ Single embedding generation
✅ Vector search operations
✅ Cache operations
✅ Health checks
✅ CRUD operations
✅ Rate limiting
✅ Authentication/authorization
```

**Characteristics:**
- Execution time: < 30 seconds
- Memory: < 3GB
- Stateless
- Event-driven

### ECS/EC2-Required Components (10%)

```
⚠️ Batch embedding generation (> 1000 items)
⚠️ Video processing (> 5 minutes)
⚠️ Model training/fine-tuning
⚠️ WebSocket server (if not using API Gateway)
⚠️ Long-running background jobs
```

**Characteristics:**
- Execution time: > 15 minutes
- Memory: > 3GB
- Stateful or long-running
- Continuous processing

---

## 📊 11. Refactoring Checklist

### Code Changes Required

```yaml
Minimal Changes:
  - ✅ FastAPI → Lambda handlers (use Mangum adapter)
  - ✅ Database connections → RDS Proxy
  - ✅ Redis → ElastiCache
  - ✅ Environment variables → Secrets Manager
  - ✅ Logging → CloudWatch Logs

Optional Changes:
  - 🔄 SentenceTransformers → Bedrock Titan Embeddings
  - 🔄 pgvector → OpenSearch (for scale)
  - 🔄 Synchronous → Async with SQS
  - 🔄 WebSocket → API Gateway WebSocket API
```

### Infrastructure as Code

```yaml
Recommended: AWS CDK (Python)

Stacks:
  - VPC Stack
  - Database Stack (Aurora + RDS Proxy)
  - Cache Stack (ElastiCache)
  - Lambda Stack (all functions)
  - API Gateway Stack
  - EventBridge Stack
  - Monitoring Stack (CloudWatch + X-Ray)
```

---

## 🚀 12. Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CloudFront CDN                        │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   API Gateway                            │
│  - REST API                                             │
│  - Lambda Authorizer (Cognito)                          │
│  - Throttling & Rate Limiting                           │
└────────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────────┐ ┌────▼─────────┐ ┌───▼──────────┐
│ Lambda:        │ │ Lambda:      │ │ Lambda:      │
│ Brand APIs     │ │ Article APIs │ │ Vector Search│
└───────┬────────┘ └────┬─────────┘ └───┬──────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────────┐ ┌────▼─────────┐ ┌───▼──────────┐
│ RDS Proxy      │ │ ElastiCache  │ │ Bedrock      │
│ (Connection    │ │ Redis        │ │ (Embeddings) │
│  Pooling)      │ │              │ │              │
└───────┬────────┘ └──────────────┘ └──────────────┘
        │
┌───────▼────────┐
│ Aurora         │
│ PostgreSQL     │
│ (pgvector)     │
└────────────────┘
```

---

## 💰 13. Cost Estimation

### Lambda Costs (Monthly)

```
Assumptions:
  - 1M API requests/month
  - Avg execution: 500ms
  - Memory: 1024MB

Lambda Compute:
  - 1M requests × $0.20 per 1M = $0.20
  - 1M × 0.5s × 1024MB = 512,000 GB-seconds
  - 512,000 × $0.0000166667 = $8.53
  - Total: $8.73/month

API Gateway:
  - 1M requests × $3.50 per 1M = $3.50/month
```

### Database Costs

```
Aurora Serverless v2:
  - Min: 0.5 ACU = ~$43/month
  - Max: 4 ACU = ~$350/month
  - Avg: 1 ACU = ~$87/month

RDS Proxy:
  - $0.015 per vCPU-hour
  - 2 vCPU × 730 hours = $21.90/month
```

### Cache Costs

```
ElastiCache Redis:
  - cache.t3.micro = $12.41/month
  - cache.t3.small = $24.82/month
```

### Total Monthly Cost

```
Development: ~$50/month
  - Lambda: $10
  - Aurora: 0.5 ACU ($43)
  - ElastiCache: t3.micro ($12)

Production: ~$150/month
  - Lambda: $50
  - Aurora: 1-2 ACU ($87)
  - ElastiCache: t3.small ($25)
  - API Gateway: $10
```

---

## ✅ 14. Conclusion

### Summary

The HiveMind backend is **90% Lambda-compatible** with minimal refactoring required. The architecture follows modern async patterns and clean separation of concerns, making AWS migration straightforward.

### Key Findings

1. **All API endpoints** can run on Lambda (< 3s execution)
2. **Vector operations** are Lambda-compatible with proper optimization
3. **Database layer** is async and works with Aurora PostgreSQL
4. **Redis caching** maps directly to ElastiCache
5. **AI components** can use Bedrock or self-hosted models

### Recommended Approach

1. **Phase 1:** Migrate API handlers to Lambda (1 week)
2. **Phase 2:** Set up Aurora + ElastiCache (3 days)
3. **Phase 3:** Replace embeddings with Bedrock (1 week)
4. **Phase 4:** Add background jobs with SQS/Step Functions (1 week)

**Total Migration Time:** 3-4 weeks

---

*Document Version: 1.0*  
*Analysis Date: 2024*  
*Backend Framework: FastAPI (Async)*  
*Target Platform: AWS Serverless*
