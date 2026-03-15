# 🏗️ Architecture Deep Dive

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                       FRONTEND (Next.js)                            │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ Social Dashboard │  │ Personalized     │  │ Video Editor     │  │
│  │ • Brand Setup    │  │ Feed             │  │ • Upload UI      │  │
│  │ • Post Preview   │  │ • Topic Filter   │  │ • Timeline View  │  │
│  │ • Analytics      │  │ • Infinite Scroll│  │ • Caption Editor │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
└────────────────┬─────────────────────────────────────────┬──────────┘
                 │ API Client (app/lib/api.ts)            │
                 └──────────────────┬─────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
    ┌───────▼────────┐    ┌─────────▼────────┐    ┌─────────▼────────┐
    │ SOCIAL MEDIA   │    │   NEWS FEED      │    │  VIDEO EDITOR    │
    │    ENGINE      │    │    PIPELINE      │    │    PIPELINE      │
    └────────────────┘    └──────────────────┘    └──────────────────┘
            │                       │                       │
    ┌───────▼────────┐    ┌─────────▼────────┐    ┌─────────▼────────┐
    │  FastAPI       │    │  FastAPI         │    │  FastAPI         │
    │  Endpoints     │    │  Endpoints       │    │  Endpoints       │
    │                │    │                  │    │                  │
    │ POST /brands   │    │ POST /ingest     │    │ POST /upload     │
    │ POST /generate │    │ GET /feed/{id}   │    │ POST /scenes     │
    │ POST /track    │    │ POST /track      │    │ POST /captions   │
    │ GET /analytics │    │ POST /tune       │    │ POST /export     │
    └────────────────┘    └──────────────────┘    └──────────────────┘
            │                       │                       │
    ┌───────▼────────┐    ┌─────────▼────────┐    ┌─────────▼────────┐
    │ AI Services    │    │ NLP Service      │    │ CV Service       │
    │                │    │                  │    │                  │
    │ • LLM          │    │ • Embeddings     │    │ • Scene Detection│
    │ • Prompts      │    │ • Topic Extract  │    │ • Face Detection │
    │ • Feedback     │    │ • Sentiment      │    │ • Thumbnail Sel  │
    │   Loop         │    │ • Similarity     │    │ • STT (Captions) │
    └────────────────┘    └──────────────────┘    └──────────────────┘
            │                       │                       │
    ┌───────▼────────┐    ┌─────────▼────────┐    ┌─────────▼────────┐
    │ SQLAlchemy     │    │ SQLAlchemy       │    │ SQLAlchemy       │
    │ Models         │    │ Models           │    │ Models           │
    │                │    │                  │    │                  │
    │ • Brand        │    │ • Article        │    │ • Video          │
    │ • Post         │    │ • UserBehavior   │    │ • VideoScene     │
    │ • Engagement   │    │ • ArticleTag     │    │ • Caption        │
    └────────────────┘    └──────────────────┘    └──────────────────┘
            │                       │                       │
            └───────────────────────┼───────────────────────┘
                                    │
                    ┌───────────────▼───────────────┐
                    │   PostgreSQL Database         │
                    │                               │
                    │ • brands                      │
                    │ • generated_posts             │
                    │ • engagement_metrics          │
                    │ • articles (with embeddings)  │
                    │ • user_behavior               │
                    │ • user_interest_embeddings    │
                    │ • videos                      │
                    │ • video_scenes (with embeddings)│
                    │ • captions                    │
                    │ • cross_module_links          │
                    │                               │
                    │ pgvector Extension Enabled    │
                    └───────────────────────────────┘
```

---

## Data Flow Patterns

### Pattern 1: Social Media Content Generation & Feedback

```
┌─────────────────────────────────────────────────────────┐
│ 1. BRAND INPUT                                          │
│    Brand keywords, tone, audience, platforms            │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 2. CONTENT GENERATION (ContentGenerationService)        │
│    • Load brand DNA                                     │
│    • Use LLM + prompt templates                         │
│    • Generate captions, hashtags, CTAs                  │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 3. STORAGE (SQLAlchemy → PostgreSQL)                    │
│    • Save GeneratedPost                                 │
│    • Mark platform, caption, hashtags                   │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 4. PUBLISHING (Mock Social API)                         │
│    • Call platform API (Instagram, LinkedIn, X)         │
│    • Update published status, post_id                   │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 5. ENGAGEMENT TRACKING                                  │
│    • Likes, comments, shares, impressions              │
│    • Click-through rate, sentiment                      │
│    • Store EngagementMetric                             │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 6. FEEDBACK LOOP (Refine Prompts)                       │
│    • Analyze EngagementMetric data                      │
│    • Identify successful patterns                       │
│    • Adjust prompt templates                            │
│    • Update Brand.prompt_version                        │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 7. NEXT GENERATION                                      │
│    • Generate content with improved prompts             │
│    • Better engagement expected                         │
│    • Cycle repeats → Compounding improvement            │
└─────────────────────────────────────────────────────────┘
```

**Cycle Time:** 1 hour - 1 week (based on posting schedule)

---

### Pattern 2: Personalized News Feed Recommendation

```
┌─────────────────────────────────────────────────────────┐
│ 1. ARTICLE INGESTION                                    │
│    • Parse article metadata                             │
│    • Extract title, body, source, URL                   │
└────────────────┬────────────────────────────────────────┘
                 │
┌─────────────────────────────────────────────────────────┐
│ 2. NLP PROCESSING (NLPService)                          │
│    • Extract topics (AI, Tech, Business, etc)          │
│    • Analyze sentiment (positive, neutral, negative)   │
│    • Generate embedding (1024-dim vector, Nova)         │
│    • Create ArticleTag entries                          │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 3. VECTOR STORAGE (pgvector)                            │
│    • Store article embedding in vector column           │
│    • Index with IVFFlat for fast similarity search      │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 4. STORAGE (Article + ArticleTag)                       │
│    • Save article metadata                              │
│    • Save topics with confidence scores                 │
│    • Embedding already stored in step 3                 │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 5. USER REQUESTS FEED                                   │
│    • GET /feed/{user_id}                                │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 6. BUILD USER PROFILE                                   │
│    • Query UserBehavior (clicks, reads)                 │
│    • Extract interests from read articles               │
│    • Aggregate embeddings with weights                  │
│    • Store in user_interest_embeddings table            │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 7. RECOMMENDATION ENGINE (Hybrid + Vector)              │
│    For each article:                                    │
│      • Vector similarity = cosine(user_emb, article_emb)│
│      • Interest match = topic overlap                   │
│      • Behavior bias = recent action history            │
│      • score = 0.5*vector_sim + 0.3*interest + 0.2*behavior│
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 8. RANK & RETURN                                        │
│    • Sort by score (highest first)                      │
│    • Use pgvector IVFFlat index for fast retrieval     │
│    • Return top N items                                 │
│    • Include relevance_score in response                │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 9. USER INTERACTION (Click, Read, Like)                 │
│    • Track action in UserBehavior                       │
│    • Store read_time, scroll_depth                      │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 10. TUNE RECOMMENDATIONS                                │
│     • POST /recommendations/tune/{user_id}              │
│     • Analyze behavior patterns                         │
│     • Update user_interest_embeddings with new weights  │
│     • Adjust weighting for next recommendation          │
│     • Build smarter user profile                        │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 11. NEXT FEED REQUEST                                   │
│     • User receives more relevant articles              │
│     • Vector similarity improves with more data         │
│     • Cycle repeats → Personalization improves          │
└─────────────────────────────────────────────────────────┘
```

**Cycle Time:** 1 second - 1 hour (per feed request)

---

### Pattern 3: Video Processing Pipeline

```
┌─────────────────────────────────────────────────────────┐
│ 1. VIDEO UPLOAD                                         │
│    • User selects file                                  │
│    • Server extracts metadata                           │
│    • Create Video record                                │
│    • Set status = "processing"                          │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 2. SCENE DETECTION (VideoProcessingService)             │
│    • Run CV algorithms                                  │
│    • Detect cuts, transitions, silences                 │
│    • Identify key moments                               │
│    • Return scenes with timing                          │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 3. STORE SCENES                                         │
│    • Create VideoScene entries                          │
│    • Scene type: cut, transition, silence, key_moment   │
│    • Confidence score: 0-100%                           │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 4. AUDIO EXTRACTION & CAPTIONING                        │
│    • Extract audio from video                           │
│    • Run speech-to-text (Whisper, Azure, GCP)          │
│    • Generate Caption entries                           │
│    • Support multiple languages                         │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 5. THUMBNAIL SELECTION                                  │
│    • Analyze video frames                               │
│    • Face detection, emotion analysis                   │
│    • Select optimal frame for CTR                       │
│    • Generate thumbnail image                           │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 6. AI SUGGESTIONS                                       │
│    • Highlight high-confidence scenes                   │
│    • Suggest cuts at silences                           │
│    • Recommend transitions                              │
│    • Provide editing tips                               │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 7. USER EDITS (Manual Step)                             │
│    • Adjust/delete captions                             │
│    • Confirm scene cuts                                 │
│    • Select thumbnail preference                        │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 8. EXPORT OPTIMIZATION                                  │
│    • Get platform preset (Instagram, YouTube, etc)      │
│    • Adjust aspect ratio (9:16, 16:9, 1:1)             │
│    • Optimize resolution & bitrate                      │
│    • Trim to platform duration limits                   │
│    • Embed captions if selected                         │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 9. RENDER & UPLOAD                                      │
│    • Queue background render job                        │
│    • Return export status                               │
│    • Notify when ready                                  │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│ 10. PERFORMANCE TRACKING                                │
│     • Track views, engagement, retention                │
│     • Learn optimal editing patterns                    │
│     • Improve future suggestions                        │
└─────────────────────────────────────────────────────────┘
```

**Cycle Time:** 2-10 minutes (per video)

---

## Database Relationships

```
User (from existing schema)
  │
  ├── Brand [One-to-Many]
  │     ├── GeneratedPost [One-to-Many]
  │     │     └── EngagementMetric [One-to-Many]
  │     └── EngagementMetric [Direct]
  │
  ├── Article (read-only ingestion)
  │     ├── ArticleTag [One-to-Many]
  │     └── UserBehavior [One-to-Many] ◄── user_id reference
  │
  └── Video [One-to-Many]
        ├── VideoScene [One-to-Many]
        └── Caption [One-to-Many]
```

---

## API Response Patterns

### Success Response (200 OK)
```json
{
  "id": 42,
  "data": {...},
  "timestamp": "2024-01-31T10:00:00Z",
  "status": "success"
}
```

### Error Response (4xx/5xx)
```json
{
  "detail": "Error message",
  "error_code": "NOT_FOUND",
  "status": 404
}
```

### List Response
```json
[
  {"id": 1, "data": {...}},
  {"id": 2, "data": {...}},
  ...
]
```

---

## Scalability Considerations

### Current (MVP)
- Single FastAPI server
- Synchronous AI operations
- In-memory caching

### V1 (Growth)
- Async job queue (Celery)
- Redis caching layer
- Database indexing
- Load balancing

### V2 (Scale)
- Microservices (separate for each module)
- Message queue (RabbitMQ, Kafka)
- Distributed caching (Redis cluster)
- Database sharding
- CDN for media

---

## Security Patterns

### Authentication
```python
# JWT-based (ready to implement)
from jose import JWTError, jwt
from datetime import timedelta

# Create token on login
token = create_access_token(user_id, expires_delta=timedelta(hours=24))

# Verify on protected endpoints
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get("sub")
```

### CORS
```python
# Allow specific origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting
```python
# Implement per endpoint
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/social/generate/content")
@limiter.limit("10/minute")
async def generate_content(...):
    ...
```

---

## Monitoring & Observability

### Logging
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Content generated for brand", extra={"brand_id": 1})
logger.error("API error", exc_info=True)
```

### Metrics to Track
- API response times
- Content generation success rate
- Feed ranking accuracy
- Video processing time
- User engagement rates
- Recommendation CTR

### Health Checks
```python
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "db_connected": check_db(),
        "redis_connected": check_redis()
    }
```

---

## Development Best Practices

### Code Organization
- Services: Business logic
- Models: Data representation
- Schemas: API contracts
- Endpoints: Route handlers
- Core: Shared utilities

### Testing Strategy
- Unit tests for services
- Integration tests for endpoints
- Mock external APIs
- Test feedback loops

### Deployment Checklist
- [ ] All tests passing
- [ ] No security vulnerabilities
- [ ] Database migrations ready
- [ ] Environment variables set
- [ ] Rate limiting configured
- [ ] Monitoring enabled
- [ ] Backups configured
- [ ] Rollback plan ready

---

## Performance Optimization Tips

### Database
- Add indexes on frequently queried columns
- Use pagination for large result sets
- Cache popular queries with Redis
- Optimize vector indexes (tune IVFFlat lists parameter)
- Use batch embedding generation (Nova Multimodal Embeddings)

### API
- Use async/await for I/O operations
- Implement request caching
- Compress responses (gzip)

### Frontend
- Lazy load components
- Optimize images
- Use service workers for offline support

---

This architecture is designed to be:
✅ **Scalable** - Handles growth from 100 to 1M users
✅ **Maintainable** - Clean, modular code
✅ **Testable** - Easy to test services
✅ **Production-Ready** - Real patterns, not toy examples
✅ **Extensible** - Easy to add new modules

---

## Amazon Nova Integration

### Model Routing

- **Nova 2 Lite** (`amazon.nova-2-lite-v1:0`) for content generation, summarization, analysis, trend and performance reasoning.
- **Nova 2 Sonic** (`amazon.nova-2-sonic-v1:0`) for voice/speech workflows (incremental rollout).
- **Nova Multimodal Embeddings** (`amazon.nova-2-multimodal-embeddings-v1:0`) for semantic search and vector retrieval.

### API Patterns

- Use `converse()` for text/reasoning paths.
- Use `invoke_model()` for embeddings with `taskType: SINGLE_EMBEDDING`.
- Use `start_async_invoke()` for long-running/batch embedding jobs.

### Vector Storage

- Canonical embedding dimension is **1024**.
- pgvector columns and ANN indexes are aligned to `vector(1024)`.

### Multimodal Input

Image understanding requests use Nova-compatible content blocks with base64 image payloads.
