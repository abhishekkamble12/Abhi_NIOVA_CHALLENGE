# 🚀 Quick Start Scripts

## Files

- **`setup.bat`** - First-time setup (run once)
- **`start.bat`** - Start all services
- **`stop.bat`** - Stop all services

## Usage

### 1. First Time Setup

```bash
setup.bat
```

This will:
- Create Python virtual environment
- Install backend dependencies (FastAPI, SQLAlchemy, etc.)
- Install frontend dependencies (Next.js, React, etc.)

### 2. Start Application

```bash
start.bat
```

This will:
- Start Backend on http://localhost:8000
- Start Frontend on http://localhost:3000
- Open browser automatically

### 3. Stop Application

```bash
stop.bat
```

This will:
- Stop backend server (port 8000)
- Stop frontend server (port 3000)

## Troubleshooting

### "Module not found" errors
Run `setup.bat` first to install dependencies

### Port already in use
Run `stop.bat` to kill existing processes

### Python/Node not found
Install Python 3.9+ and Node.js 18+ and add to PATH

## Manual Commands

If batch files don't work, run manually:

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy aiosqlite pydantic-settings python-dotenv
python run.py
```

### Frontend
```bash
npm install
npm run dev
```
