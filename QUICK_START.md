# 🚀 Quick Start Guide

## System Requirements
- Python 3.9 or higher
- Node.js 18 or higher
- PostgreSQL 12 or higher (optional, can use SQLite for testing)
- Git

## Setup Instructions

### 1. Clone & Navigate
```bash
git clone <repo-url>
cd aws
```

### 2. Backend Setup (FastAPI)

#### Create Virtual Environment
```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

#### Run Database Migrations (if needed)
```bash
# Optional: Create tables
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

#### Start Backend Server
```bash
python run.py
```

**Backend URL:** `http://localhost:8000`
**API Docs:** `http://localhost:8000/docs` (Swagger)

---

### 3. Frontend Setup (Next.js)

#### Navigate to Frontend
```bash
cd ../app
```

#### Install Dependencies
```bash
npm install
```

#### Configure Environment
```bash
cp .env.example .env.local
# env.local already points to http://localhost:8000/api/v1
```

#### Start Frontend Server
```bash
npm run dev
```

**Frontend URL:** `http://localhost:3000`

---

## 🎯 First Steps (Demo Flow)

### Module 1: Social Media Engine
1. Open http://localhost:3000
2. Click "📱 Social Media" tab
3. Click "+ New Brand"
4. Fill in brand details:
   - Name: "TechStartup"
   - Keywords: ["AI", "SaaS", "Technology"]
   - Tone: "professional"
   - Platforms: ["instagram", "linkedin", "x"]
5. Click "✨ instagram" to generate content
6. See generated posts with captions, hashtags, CTAs
7. Click "📤 Publish Now" to simulate publishing
8. Click "🔄 Optimize Prompts" to trigger feedback loop

### Module 2: Personalized News Feed
1. Click "📰 News Feed" tab
2. Articles load (mock data)
3. See relevance scores for each article
4. Click on article to track behavior
5. Use topic filters to refine feed
6. Click "🔄 Refresh Feed" to re-rank based on learning
7. Click "🧠 AI Tune Recommendations" to trigger optimization

### Module 3: Video Editor
1. Click "🎬 Video Editor" tab
2. Click "+ Choose Video" to upload
3. System detects scenes automatically
4. Review and edit captions
5. Select optimal thumbnail
6. Choose platform (Instagram Reels, YouTube Shorts, etc.)
7. Click export button

---

## 📊 API Testing with cURL

### Generate Social Content
```bash
curl -X POST "http://localhost:8000/api/v1/social/generate/content?brand_id=1&platform=instagram" \
  -H "Content-Type: application/json"
```

### Get Personalized Feed
```bash
curl "http://localhost:8000/api/v1/feed/feed/1?limit=20"
```

### Detect Scenes in Video
```bash
curl -X POST "http://localhost:8000/api/v1/videos/videos/1/detect-scenes"
```

### Track Engagement
```bash
curl -X POST "http://localhost:8000/api/v1/social/track/engagement/1?likes=50&comments=10&shares=5&impressions=1000&ctr=5.0"
```

---

## 📝 API Documentation

**Swagger UI:** `http://localhost:8000/docs`
**ReDoc:** `http://localhost:8000/redoc`

All endpoints are documented with:
- Request/Response examples
- Parameter descriptions
- Error codes

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd app
npm test
```

---

## 🔧 Development Tips

### Code Structure
- Backend: FastAPI async-first design
- Frontend: React functional components with hooks
- Services: Modular, testable, mockable

### Adding New Features
1. Add model in `backend/app/models/`
2. Add schema in `backend/app/schemas/`
3. Add service logic in `backend/app/services/`
4. Add endpoints in `backend/app/api/v1/endpoints/`
5. Add frontend component in `app/components/`
6. Update API client in `app/lib/api.ts`

### Database Access
```python
# In backend endpoints
from app.core.database import get_db
from sqlalchemy.orm import Session

async def my_endpoint(db: Session = Depends(get_db)):
    # Query database
    result = db.query(MyModel).all()
    return result
```

### Calling API from Frontend
```typescript
// In React components
import { apiClient } from '@/lib/api';

const data = await apiClient.brand.list();
const post = await apiClient.content.generate(brandId, 'instagram');
```

---

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Check if port 8000 is already in use
# Option 1: Kill process on port 8000
# Windows: netstat -ano | findstr :8000
# macOS/Linux: lsof -i :8000

# Option 2: Change port in run.py
```

### Frontend Can't Connect to Backend
```bash
# Check:
1. Backend is running: http://localhost:8000
2. CORS is enabled in backend
3. API_URL in .env.local is correct: http://localhost:8000/api/v1
```

### Database Connection Error
```bash
# Check PostgreSQL is running
# Update DATABASE_URL in .env
# Or use SQLite: DATABASE_URL=sqlite:///./test.db
```

### Port Already in Use
```bash
# Frontend (change port in package.json or CLI)
npm run dev -- -p 3001

# Backend (change in run.py or use)
uvicorn app.main:app --reload --port 8001
```

---

## 📦 Project Structure Reference

```
ai-media-platform/
├── backend/                    # FastAPI
│   ├── app/
│   │   ├── api/v1/endpoints/  # API routes
│   │   ├── models/            # Database models
│   │   ├── schemas/           # Request/Response schemas
│   │   ├── services/          # Business logic
│   │   ├── core/              # Database, config
│   │   └── main.py
│   ├── requirements.txt
│   └── run.py
│
├── app/                       # Next.js Frontend
│   ├── components/            # React components
│   ├── lib/                   # Utilities (API client)
│   ├── app/                   # App router
│   ├── package.json
│   └── .env.example
│
└── PROJECT_DOCUMENTATION.md   # Full docs
```

---

## 🎓 Learning Resources

### Backend (FastAPI)
- FastAPI docs: https://fastapi.tiangolo.com
- SQLAlchemy: https://docs.sqlalchemy.org

### Frontend (Next.js + React)
- Next.js: https://nextjs.org/docs
- React: https://react.dev
- Framer Motion: https://www.framer.com/motion

### AI/ML Integration
- OpenAI API: https://platform.openai.com/docs
- Hugging Face: https://huggingface.co

---

## 📋 Checklist for Demo/Presentation

- [ ] Backend running on localhost:8000
- [ ] Frontend running on localhost:3000
- [ ] Create a test brand
- [ ] Generate social content
- [ ] View generated posts
- [ ] Publish content
- [ ] Track engagement
- [ ] View personalized feed
- [ ] Upload/process video
- [ ] View optimized export options

---

## 🚀 Deployment Preparation

### Before Production:
1. Add proper authentication (JWT)
2. Set up real database (PostgreSQL)
3. Configure CORS properly
4. Add rate limiting
5. Set up SSL/TLS
6. Add API key management
7. Configure real LLM APIs
8. Set up monitoring & logging
9. Add error tracking (Sentry)
10. Set up CI/CD pipeline

### Deployment Options:
- Backend: Heroku, AWS EC2, DigitalOcean, Railway
- Frontend: Vercel, Netlify, AWS S3 + CloudFront
- Database: AWS RDS, Heroku Postgres, DigitalOcean

---

## 💡 Next Steps

1. **Try the platform** - Explore all three modules
2. **Review code** - Check implementation patterns
3. **Modify & extend** - Add your own features
4. **Connect real APIs** - Replace mock services
5. **Scale it up** - Add authentication, multi-user, better DB

---

## 🤝 Support

- Check `PROJECT_DOCUMENTATION.md` for detailed info
- Review API docs at `http://localhost:8000/docs`
- Check browser console for frontend errors
- Check backend logs in terminal

---

**Happy building! 🎉**
