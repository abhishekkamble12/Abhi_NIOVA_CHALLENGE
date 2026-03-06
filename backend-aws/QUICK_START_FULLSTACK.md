# 🚀 Quick Start - Full Stack

## Setup (One Time)

### 1. Backend Setup
```bash
cd backend-aws

# Install dependencies
python3.11 -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Add your AWS credentials and endpoints
```

### 2. Database Setup
```bash
# Connect to Aurora
psql -h $DB_HOST -U $DB_USER -d $DB_NAME

# Run schema
\i schema.sql
\q
```

### 3. Frontend Setup
```bash
cd ../aws

# Install dependencies
npm install

# Configure
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
```

---

## Running (Every Time)

### Terminal 1: Backend
```bash
cd backend-aws
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1
./run_server.sh           # Windows: .\run_server.ps1
```

Backend runs on: **http://localhost:8000**  
API Docs: **http://localhost:8000/docs**

### Terminal 2: Frontend
```bash
cd aws
npm run dev
```

Frontend runs on: **http://localhost:3000**

---

## Verify Connection

### 1. Check Backend Health
```bash
curl http://localhost:8000/health
```

Expected:
```json
{
  "status": "healthy",
  "services": {
    "aurora": "✅ connected",
    "redis": "✅ connected"
  }
}
```

### 2. Test API from Frontend
Open http://localhost:3000 and:
- Create a brand (Social Media tab)
- Generate content
- Search news (News Feed tab)
- Upload video (Video Editor tab)

---

## Architecture

```
Frontend (localhost:3000)
    ↓ HTTP REST
Backend API (localhost:8000)
    ↓
AWS Services
    ├─→ Aurora PostgreSQL (ap-south-1)
    ├─→ ElastiCache Redis (ap-south-1)
    ├─→ S3 (ap-south-1)
    ├─→ Bedrock (ap-south-1)
    └─→ EventBridge (ap-south-1)
```

---

## Troubleshooting

### Backend won't start
```bash
# Check .env file exists
cat .env

# Check dependencies
pip list | grep fastapi

# Check port 8000 is free
lsof -i :8000  # Unix
netstat -ano | findstr :8000  # Windows
```

### Frontend can't connect
```bash
# Check .env.local
cat .env.local

# Should be:
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Restart frontend
npm run dev
```

### Database errors
```bash
# Test connection
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1"

# Check schema
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\dt"
```

---

## Quick Commands

```bash
# Backend
cd backend-aws && ./run_server.sh

# Frontend
cd aws && npm run dev

# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs

# Frontend
open http://localhost:3000
```

---

## 🎯 Success Checklist

- [ ] Backend starts on port 8000
- [ ] Frontend starts on port 3000
- [ ] Health check returns ✅ for Aurora and Redis
- [ ] Can create brand in frontend
- [ ] Can search news in frontend
- [ ] Can upload video in frontend
- [ ] API docs accessible at /docs

---

## 📚 Documentation

- **Backend API**: See `FRONTEND_INTEGRATION.md`
- **AWS Services**: See `EC2_DEPLOYMENT.md`
- **Database Schema**: See `schema.sql`
- **Frontend API Client**: See `aws/app/lib/api.ts`
