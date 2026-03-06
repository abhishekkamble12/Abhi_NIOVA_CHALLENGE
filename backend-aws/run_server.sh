#!/bin/bash
# Start HiveMind Backend Server

set -e

echo "=========================================="
echo "🚀 Starting HiveMind Backend Server"
echo "=========================================="

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Run ./deploy.sh first"
    exit 1
fi

# Check .env
if [ ! -f .env ]; then
    echo "❌ .env file not found"
    exit 1
fi

# Load environment
export $(grep -v '^#' .env | xargs)

echo "✅ Environment loaded"
echo "✅ Starting FastAPI server on port 8000..."
echo ""

# Start server
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
