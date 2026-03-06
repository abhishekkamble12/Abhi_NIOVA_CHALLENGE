# HiveMind Backend - Frontend Integration

## 🎯 Architecture

```
Frontend (Next.js)
    ↓ HTTP/REST
FastAPI Server (api_server.py)
    ↓
AWS Services (backend-aws/)
    ├─→ Aurora PostgreSQL
    ├─→ ElastiCache Redis
    ├─→ S3
    ├─→ Bedrock
    └─→ EventBridge
```

---

## 🚀 Quick Start

### 1. Setup Database

```bash
# Connect to Aurora
psql -h $DB_HOST -U $DB_USER -d $DB_NAME

# Run schema
\i schema.sql
```

### 2. Configure Environment

```bash
# backend-aws/.env
AWS_REGION=ap-south-1
DB_HOST=your-aurora-endpoint
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=hiveminddb
REDIS_HOST=your-redis-endpoint
S3_BUCKET=hivemind-media
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
NEWS_API_KEY=your_newsapi_key
```

### 3. Start Backend

```bash
cd backend-aws
source venv/bin/activate
pip install fastapi uvicorn
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

### 4. Configure Frontend

```bash
# aws/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 5. Start Frontend

```bash
cd aws
npm install
npm run dev
```

---

## 📡 API Endpoints

### Social Media (`/api/v1/social`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/brands` | Create brand |
| GET | `/brands/{id}` | Get brand |
| GET | `/brands` | List brands |
| POST | `/generate/content?brand_id=X&platform=Y` | Generate content |
| GET | `/posts/{id}` | Get post |
| GET | `/brand/{id}/posts` | Get brand posts |
| PUT | `/posts/{id}/publish` | Publish post |
| POST | `/track/engagement/{id}` | Track engagement |
| GET | `/analytics/brand/{id}` | Get analytics |

### News Feed (`/api/v1/feed`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/articles/ingest` | Ingest article |
| GET | `/articles/{id}` | Get article |
| GET | `/feed/{user_id}` | Get personalized feed |
| GET | `/real/search?keyword=X` | Search news |
| GET | `/real/trending?country=us` | Get trending |
| GET | `/real/personalized/{user_id}` | Get personalized |
| GET | `/real/category/{category}` | Get by category |
| POST | `/real/summarize` | Summarize article |
| GET | `/real/preferences/{user_id}` | Get preferences |
| POST | `/real/preferences/{user_id}` | Create preferences |
| PUT | `/real/preferences/{user_id}` | Update preferences |

### Videos (`/api/v1/videos`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/videos/upload` | Upload video |
| GET | `/videos/{id}` | Get video |
| POST | `/videos/{id}/detect-scenes` | Detect scenes |
| GET | `/videos/{id}/scenes` | Get scenes |
| POST | `/videos/{id}/generate-captions` | Generate captions |
| GET | `/videos/{id}/captions` | Get captions |
| PUT | `/captions/{id}?new_text=X` | Edit caption |
| POST | `/videos/{id}/select-thumbnail` | Select thumbnail |
| GET | `/export-presets` | Get presets |
| POST | `/videos/{id}/export` | Export video |
| GET | `/videos/{id}/suggestions` | Get suggestions |

---

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### Create Brand
```bash
curl -X POST http://localhost:8000/api/v1/social/brands \
  -H "Content-Type: application/json" \
  -d '{
    "name": "TechCorp",
    "industry": "Technology",
    "tone": "Professional",
    "target_audience": "Developers"
  }'
```

### Generate Content
```bash
curl -X POST "http://localhost:8000/api/v1/social/generate/content?brand_id=1&platform=linkedin"
```

### Search News
```bash
curl "http://localhost:8000/api/v1/feed/real/search?keyword=AI&limit=5"
```

### Upload Video
```bash
curl -X POST http://localhost:8000/api/v1/videos/videos/upload \
  -F "file=@video.mp4"
```

---

## 🔧 Frontend Integration

The frontend (`app/lib/api.ts`) is already configured to call these endpoints:

```typescript
// Example: Generate content
const result = await apiClient.content.generate(brandId, 'linkedin');

// Example: Search news
const articles = await apiClient.feed.searchNews('AI', 'publishedAt', 20);

// Example: Upload video
const formData = new FormData();
formData.append('file', videoFile);
const video = await apiClient.videos.upload(formData);
```

---

## 📊 Data Flow

### Social Media Flow
```
1. Frontend → POST /brands → Create brand
2. Frontend → POST /generate/content → Bedrock generates content
3. Backend → Store in Aurora
4. Backend → Publish to EventBridge
5. Frontend → GET /posts/{id} → Display post
```

### News Feed Flow
```
1. Frontend → GET /real/search → NewsAPI
2. Backend → Return articles
3. Frontend → POST /real/summarize → Bedrock summarizes
4. Backend → Return summary
```

### Video Flow
```
1. Frontend → POST /videos/upload → Upload to S3
2. Backend → Store metadata in Aurora
3. Frontend → POST /detect-scenes → Detect scenes
4. Frontend → POST /generate-captions → Bedrock generates
5. Frontend → POST /export → Export video
```

---

## ✅ Verification

1. **Backend Running**: `curl http://localhost:8000/health`
2. **Database Connected**: Check health response shows Aurora ✅
3. **Redis Connected**: Check health response shows Redis ✅
4. **Frontend Connected**: Open http://localhost:3000
5. **API Calls Work**: Test any endpoint from frontend

---

## 🎯 Summary

✅ FastAPI server connects AWS services to frontend  
✅ All frontend API calls mapped to backend endpoints  
✅ Database schema created for all features  
✅ Bedrock integration for AI features  
✅ S3 integration for file uploads  
✅ EventBridge integration for events  
✅ Redis caching for performance  

**Start command**: `uvicorn api_server:app --reload --host 0.0.0.0 --port 8000`
