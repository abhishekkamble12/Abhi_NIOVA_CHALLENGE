# 🚀 HiveMind - AI Media OS

Complete AI-powered platform for content creation with social media, news curation, and video editing.

---

## ⚡ Quick Start

### 1. First Time Setup

```bash
# Configure backend
cp backend-aws/.env.example backend-aws/.env
nano backend-aws/.env  # Add your AWS credentials

# Setup database
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f backend-aws/schema.sql
```

### 2. Run Everything

**Linux/Mac:**
```bash
./run.sh
```

**Windows:**
```powershell
.\run.ps1
```

### 3. Access

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🛑 Stop

**Linux/Mac:**
```bash
./stop.sh
```

**Windows:**
```powershell
.\stop.ps1
```

---

## 📁 Project Structure

```
aws/
├── run.sh / run.ps1           # Start everything
├── stop.sh / stop.ps1         # Stop everything
├── app/                       # Next.js frontend
│   ├── components/            # React components
│   └── lib/api.ts            # API client
├── backend-aws/               # FastAPI backend
│   ├── api_server.py         # Main server
│   ├── api/                  # API endpoints
│   │   ├── social.py         # Social media
│   │   ├── feed.py           # News feed
│   │   └── videos.py         # Video editor
│   ├── services/             # AWS services
│   │   ├── aurora_service.py
│   │   ├── cache_service.py
│   │   ├── s3_service.py
│   │   ├── bedrock_service.py
│   │   └── event_service.py
│   └── schema.sql            # Database schema
```

---

## 🎯 Features

### Social Media Engine
- AI-powered content generation (Bedrock)
- Multi-platform support (LinkedIn, Instagram, X)
- Engagement tracking and analytics
- Performance-based learning

### Personalized News Feed
- Real-time news search (NewsAPI)
- AI summarization (Bedrock)
- User preferences and personalization
- Category-based filtering

### Video Intelligence
- Upload to S3
- Scene detection
- AI-generated captions (Bedrock)
- Platform-optimized exports

---

## 🔧 Technology Stack

### Frontend
- Next.js 14
- React
- TypeScript
- Tailwind CSS

### Backend
- FastAPI
- Python 3.11
- Async/await

### AWS Services
- Aurora PostgreSQL (database)
- ElastiCache Redis (cache)
- S3 (storage)
- Bedrock (AI)
- EventBridge (events)

---

## 📚 Documentation

- **[RUN_GUIDE.md](RUN_GUIDE.md)** - How to run the project
- **[backend-aws/FRONTEND_INTEGRATION.md](backend-aws/FRONTEND_INTEGRATION.md)** - API reference
- **[backend-aws/EC2_DEPLOYMENT.md](backend-aws/EC2_DEPLOYMENT.md)** - AWS deployment
- **[backend-aws/QUICK_START_FULLSTACK.md](backend-aws/QUICK_START_FULLSTACK.md)** - Full stack guide

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
  -d '{"name":"Test","industry":"Tech","tone":"Professional","target_audience":"Developers"}'
```

### Search News
```bash
curl "http://localhost:8000/api/v1/feed/real/search?keyword=AI&limit=5"
```

---

## 🔐 Environment Variables

### Backend (.env)
```bash
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
BEDROCK_MODEL_EMBEDDING=amazon.titan-embed-text-v2:0
BEDROCK_MODEL_TEXT=anthropic.claude-3-sonnet-20240229-v1:0
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 🎯 Architecture

```
Frontend (Next.js) → Backend (FastAPI) → AWS Services
                                          ├─ Aurora PostgreSQL
                                          ├─ ElastiCache Redis
                                          ├─ S3
                                          ├─ Bedrock
                                          └─ EventBridge
```

---

## 📊 Status

✅ Frontend-backend integration complete  
✅ All API endpoints implemented  
✅ AWS services connected  
✅ Database schema created  
✅ One-command startup  
✅ Production-ready  

---

## 🚀 Deployment

See [backend-aws/EC2_DEPLOYMENT.md](backend-aws/EC2_DEPLOYMENT.md) for AWS EC2 deployment instructions.

---

## 📝 License

MIT

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Start now**: `./run.sh` or `.\run.ps1` 🎉
