# 🔄 Database Connection Workflow

## Complete System Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                                │
│                  (Frontend / API / CLI)                             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       API GATEWAY                                   │
│  https://wcp5c3ga8b.execute-api.ap-south-1.amazonaws.com/prod     │
│                                                                     │
│  Routes:                                                            │
│    POST   /social/brands          → social_create_brand            │
│    GET    /social/brands          → social_list_brands             │
│    GET    /social/brands/{id}     → social_get_brand               │
│    GET    /social/posts/{id}      → social_get_post                │
│    POST   /social/generate        → social_generate_content        │
│    GET    /feed/personalized      → feed_personalized              │
│    POST   /video/upload           → video_upload_handler           │
│    POST   /ai/generate            → ai_generate_content            │
│    POST   /ai/process-video       → ai_process_video               │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      LAMBDA FUNCTIONS                               │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Function: hivemind-social-list-brands                       │ │
│  │  Runtime: Python 3.11                                        │ │
│  │  Memory: 512 MB                                              │ │
│  │  Timeout: 30s                                                │ │
│  │                                                              │ │
│  │  Environment Variables:                                      │ │
│  │    S3_BUCKET=media-ai-content                                │ │
│  │    DB_HOST=hivemind-aurora-cluster.xxxxx.rds.amazonaws.com   │ │
│  │    DB_PORT=5432                                              │ │
│  │    DB_NAME=hiveminddb                                        │ │
│  │    DB_USER=hivemind                                          │ │
│  │    DB_PASSWORD=***                                           │ │
│  │                                                              │ │
│  │  Code Flow:                                                  │ │
│  │    1. Import database_service                                │ │
│  │    2. Call list_brands()                                     │ │
│  │    3. Return success_response() with CORS headers            │ │
│  └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DATABASE SERVICE                                 │
│                  (services/database_service.py)                     │
│                                                                     │
│  def list_brands(limit: int = 100):                                │
│      with db_connection() as conn:                                 │
│          cursor = conn.cursor(cursor_factory=RealDictCursor)       │
│          cursor.execute(                                           │
│              "SELECT * FROM brands ORDER BY created_at DESC"       │
│          )                                                          │
│          return [dict(row) for row in cursor.fetchall()]           │
│                                                                     │
│  Connection Pool:                                                   │
│    • psycopg2 with context managers                                │
│    • Auto-commit on success                                        │
│    • Auto-rollback on error                                        │
│    • Connection timeout: 5s                                        │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  AURORA POSTGRESQL                                  │
│                    Serverless v2                                    │
│                                                                     │
│  Cluster: hivemind-aurora-cluster                                  │
│  Instance: hivemind-aurora-instance                                │
│  Engine: aurora-postgresql 15.4                                    │
│  Scaling: 0.5 - 1 ACU                                              │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Database: hiveminddb                                        │ │
│  │                                                              │ │
│  │  Tables:                                                     │ │
│  │    ├── brands (id, name, industry, tone, created_at)        │ │
│  │    ├── social_posts (id, brand_id, platform, content)       │ │
│  │    ├── post_engagement (id, post_id, likes, comments)       │ │
│  │    ├── articles (id, title, url, embedding)                 │ │
│  │    ├── videos (id, s3_url, duration, thumbnail)             │ │
│  │    ├── video_scenes (id, video_id, start_time, embedding)   │ │
│  │    ├── video_captions (id, video_id, text, language)        │ │
│  │    ├── user_preferences (id, user_id, keywords)             │ │
│  │    ├── user_interest_embeddings (vector)                    │ │
│  │    ├── content_similarity_cache                             │ │
│  │    └── cross_module_links                                   │ │
│  │                                                              │ │
│  │  Extensions:                                                 │ │
│  │    └── pgvector (for AI embeddings)                         │ │
│  │                                                              │ │
│  │  Indexes:                                                    │ │
│  │    ├── articles_embedding_idx (IVFFlat)                     │ │
│  │    ├── video_scenes_embedding_idx (IVFFlat)                 │ │
│  │    ├── idx_social_posts_brand (B-tree)                      │ │
│  │    └── idx_videos_created (B-tree)                          │ │
│  └──────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Deployment Workflow

```
START
  │
  ▼
┌─────────────────────────────────────┐
│  1. Deploy Aurora Cluster           │
│     (deploy-database.ps1)           │
│                                     │
│  • Create VPC resources             │
│  • Create subnet group              │
│  • Create security group            │
│  • Create Aurora cluster            │
│  • Create Aurora instance           │
│  • Wait for availability (~10 min)  │
│  • Save credentials to db-config    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  2. Initialize Schema               │
│     (setup-database-schema.ps1)     │
│                                     │
│  • Connect via psql                 │
│  • Enable pgvector extension        │
│  • Run schema.sql (base tables)     │
│  • Run schema_vector.sql (AI)       │
│  • Create indexes                   │
│  • Verify table creation            │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  3. Update Lambda Functions         │
│     (update-lambda-db-config.ps1)   │
│                                     │
│  • Load db-config.env               │
│  • List all Lambda functions        │
│  • Update environment variables     │
│  • Set DB_HOST, DB_PORT, etc.       │
│  • Wait for updates to propagate    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  4. Verify System                   │
│     (verify-system.ps1)             │
│                                     │
│  • Check database config            │
│  • Check Aurora status              │
│  • Check Lambda functions           │
│  • Test direct DB connection        │
│  • Test Lambda → DB connection      │
│  • Test API Gateway → Lambda → DB   │
│  • Check pgvector extension         │
└──────────────┬──────────────────────┘
               │
               ▼
             DONE
```

---

## Data Flow Example: Create Brand

```
1. USER
   │
   │  POST /social/brands
   │  {
   │    "name": "TechCorp",
   │    "industry": "Technology"
   │  }
   │
   ▼
2. API GATEWAY
   │
   │  Route: POST /social/brands
   │  Integration: AWS_PROXY
   │  Target: hivemind-social-create-brand
   │
   ▼
3. LAMBDA FUNCTION
   │
   │  handler.py:
   │    def handler(event, context):
   │        body = json.loads(event['body'])
   │        brand = database_service.create_brand(
   │            brand_id=str(uuid.uuid4()),
   │            name=body['name'],
   │            industry=body['industry']
   │        )
   │        return success_response(brand)
   │
   ▼
4. DATABASE SERVICE
   │
   │  database_service.py:
   │    def create_brand(brand_id, name, industry):
   │        with db_connection() as conn:
   │            cursor = conn.cursor()
   │            cursor.execute(
   │                "INSERT INTO brands VALUES (%s, %s, %s)",
   │                (brand_id, name, industry)
   │            )
   │            return cursor.fetchone()
   │
   ▼
5. AURORA POSTGRESQL
   │
   │  SQL:
   │    INSERT INTO brands (id, name, industry, created_at)
   │    VALUES ('uuid', 'TechCorp', 'Technology', NOW())
   │    RETURNING *;
   │
   │  Result:
   │    {
   │      "id": "uuid",
   │      "name": "TechCorp",
   │      "industry": "Technology",
   │      "created_at": "2024-01-01T00:00:00Z"
   │    }
   │
   ▼
6. RESPONSE
   │
   │  Status: 200
   │  Headers:
   │    Access-Control-Allow-Origin: *
   │    Content-Type: application/json
   │  Body:
   │    {
   │      "brand": {
   │        "id": "uuid",
   │        "name": "TechCorp",
   │        "industry": "Technology",
   │        "created_at": "2024-01-01T00:00:00Z"
   │      }
   │    }
   │
   ▼
7. USER
   Brand created successfully!
```

---

## Vector Search Flow Example

```
1. USER
   │
   │  GET /feed/personalized?user_id=123
   │
   ▼
2. LAMBDA: feed_personalized
   │
   │  1. Get user interest embedding
   │     SELECT embedding FROM user_interest_embeddings
   │     WHERE user_id = 123
   │
   │  2. Find similar articles
   │     SELECT id, 1 - (embedding <=> user_embedding) as similarity
   │     FROM articles
   │     WHERE embedding IS NOT NULL
   │     ORDER BY embedding <=> user_embedding
   │     LIMIT 20
   │
   │  3. Return personalized feed
   │
   ▼
3. AURORA POSTGRESQL
   │
   │  pgvector performs:
   │    • Vector similarity search (cosine distance)
   │    • IVFFlat index lookup (fast approximate search)
   │    • Returns top 20 most similar articles
   │
   ▼
4. RESPONSE
   │
   │  {
   │    "articles": [
   │      {
   │        "id": 1,
   │        "title": "AI Trends 2024",
   │        "similarity": 0.92
   │      },
   │      {
   │        "id": 2,
   │        "title": "Tech Innovation",
   │        "similarity": 0.87
   │      }
   │    ]
   │  }
```

---

## Cross-Module Intelligence Flow

```
┌──────────────┐
│   Article    │  "AI revolutionizes content creation"
│  (embedding) │
└──────┬───────┘
       │
       │  Semantic similarity search
       │
       ▼
┌──────────────────────────────────────────┐
│     cross_module_links table             │
│                                          │
│  Links articles to posts to videos       │
│  based on semantic similarity            │
└──────┬───────────────────────────────────┘
       │
       ├─────────────────┬─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Social Post  │  │ Social Post  │  │    Video     │
│  (similar)   │  │  (similar)   │  │  (similar)   │
└──────────────┘  └──────────────┘  └──────────────┘

Result: System learns that:
  • Article about AI → Generate AI-themed social posts
  • High-performing posts → Suggest similar video topics
  • Video transcripts → Recommend related articles
```

---

## Monitoring & Logging Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      CloudWatch                             │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Lambda Logs                                        │   │
│  │  /aws/lambda/hivemind-social-list-brands            │   │
│  │                                                     │   │
│  │  [INFO] Connecting to database...                  │   │
│  │  [INFO] Executing query: SELECT * FROM brands      │   │
│  │  [INFO] Returned 5 brands                          │   │
│  │  [INFO] Response time: 45ms                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  RDS Metrics                                        │   │
│  │                                                     │   │
│  │  DatabaseConnections: 3                            │   │
│  │  CPUUtilization: 12%                               │   │
│  │  ReadLatency: 2ms                                  │   │
│  │  WriteLatency: 3ms                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  API Gateway Logs                                   │   │
│  │                                                     │   │
│  │  GET /social/brands - 200 - 52ms                   │   │
│  │  POST /social/brands - 201 - 78ms                  │   │
│  │  GET /feed/personalized - 200 - 145ms              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

**Status**: ✅ Complete
**Architecture**: Serverless, Event-Driven, Cloud-Native
**Scalability**: Auto-scales from 0 to millions of requests
**Cost**: ~$35/month (dev), ~$100/month (prod)
