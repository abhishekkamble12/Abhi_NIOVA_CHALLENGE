# 🚀 HiveMind - One Command Start

## Quick Start

### Linux/Mac
```bash
./run.sh
```

### Windows
```powershell
.\run.ps1
```

---

## What It Does

1. ✅ Checks if backend virtual environment exists (creates if needed)
2. ✅ Installs backend dependencies (if needed)
3. ✅ Checks if frontend node_modules exists (installs if needed)
4. ✅ Creates frontend .env.local (if needed)
5. ✅ Starts backend on port 8000
6. ✅ Waits for backend to be ready
7. ✅ Starts frontend on port 3000
8. ✅ Shows all URLs and logs

---

## URLs

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Stop

### Linux/Mac
```bash
./stop.sh
```

### Windows
```powershell
.\stop.ps1
```

Or press `Ctrl+C` in the terminal

---

## Logs

### Linux/Mac
```bash
# Backend logs
tail -f backend-aws/backend.log

# Frontend logs
tail -f frontend.log
```

### Windows
```powershell
# View job output
Get-Job | Receive-Job
```

---

## Prerequisites

### First Time Setup

1. **Configure Backend**
```bash
cp backend-aws/.env.example backend-aws/.env
nano backend-aws/.env  # Add your AWS credentials
```

2. **Setup Database**
```bash
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f backend-aws/schema.sql
```

3. **Run**
```bash
./run.sh  # Linux/Mac
.\run.ps1  # Windows
```

---

## Troubleshooting

### Port already in use
```bash
# Linux/Mac
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9

# Windows
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess | Stop-Process
```

### Backend won't start
```bash
# Check .env exists
ls backend-aws/.env

# Check dependencies
cd backend-aws
source venv/bin/activate
pip list
```

### Frontend won't start
```bash
# Check node_modules
ls node_modules

# Reinstall
rm -rf node_modules
npm install
```

---

## Manual Start (Alternative)

### Terminal 1: Backend
```bash
cd backend-aws
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Frontend
```bash
npm run dev
```

---

## Summary

✅ **One command** to start everything  
✅ **Auto-setup** on first run  
✅ **Background processes** for both services  
✅ **Health checks** before starting frontend  
✅ **Easy stop** with stop script  
✅ **Log files** for debugging  

**Start**: `./run.sh` or `.\run.ps1`  
**Stop**: `./stop.sh` or `.\stop.ps1`  
**Access**: http://localhost:3000
