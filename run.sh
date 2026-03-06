#!/bin/bash
# HiveMind - Start Everything

set -e

echo "=========================================="
echo "🚀 HiveMind - Starting Full Stack"
echo "=========================================="

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend-aws"
FRONTEND_DIR="$SCRIPT_DIR"

# Check if backend exists
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ Backend directory not found"
    exit 1
fi

# Setup backend if needed
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo "📦 Setting up backend..."
    cd "$BACKEND_DIR"
    python3.11 -m venv venv
    source venv/bin/activate
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    echo "✅ Backend setup complete"
fi

# Check backend .env
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo "❌ Backend .env not found"
    echo "Run: cp backend-aws/.env.example backend-aws/.env"
    exit 1
fi

# Check frontend .env.local
if [ ! -f "$FRONTEND_DIR/.env.local" ]; then
    echo "📝 Creating frontend .env.local..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > "$FRONTEND_DIR/.env.local"
fi

# Install frontend dependencies if needed
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd "$FRONTEND_DIR"
    npm install
    echo "✅ Frontend setup complete"
fi

# Start backend in background
echo ""
echo "🔧 Starting Backend (port 8000)..."
cd "$BACKEND_DIR"
source venv/bin/activate
export $(grep -v '^#' .env | xargs)
uvicorn api_server:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait for backend to be ready
echo "⏳ Waiting for backend..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend ready"
        break
    fi
    sleep 1
done

# Start frontend in background
echo ""
echo "🎨 Starting Frontend (port 3000)..."
cd "$FRONTEND_DIR"
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"

# Save PIDs
echo "$BACKEND_PID" > "$SCRIPT_DIR/.backend.pid"
echo "$FRONTEND_PID" > "$SCRIPT_DIR/.frontend.pid"

echo ""
echo "=========================================="
echo "✅ HiveMind Running"
echo "=========================================="
echo ""
echo "🔗 Frontend:  http://localhost:3000"
echo "🔗 Backend:   http://localhost:8000"
echo "🔗 API Docs:  http://localhost:8000/docs"
echo ""
echo "📋 Logs:"
echo "   Backend:  tail -f backend-aws/backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "🛑 Stop: ./stop.sh"
echo ""
echo "=========================================="

# Keep script running
wait
