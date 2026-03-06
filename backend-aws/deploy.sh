#!/bin/bash
# HiveMind Backend - EC2 Deployment Script

set -e

echo "=========================================="
echo "🚀 HiveMind Backend - EC2 Setup"
echo "=========================================="

# Check if running on EC2
if [ ! -f /sys/hypervisor/uuid ] || ! grep -q ec2 /sys/hypervisor/uuid 2>/dev/null; then
    echo "⚠️  Warning: Not running on EC2"
fi

# Install Python 3.11 if needed
if ! command -v python3.11 &> /dev/null; then
    echo "Installing Python 3.11..."
    sudo yum update -y
    sudo yum install python3.11 python3.11-pip -y
fi

echo "✅ Python 3.11 installed"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3.11 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Dependencies installed"

# Check .env file
if [ ! -f .env ]; then
    echo "❌ .env file not found"
    echo "Creating from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration"
    exit 1
fi

echo "✅ Environment configured"

# Run health check
echo ""
echo "=========================================="
echo "🧪 Running Health Checks"
echo "=========================================="

python start.py

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Backend is ready!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "  1. Run: python start.py"
    echo "  2. Or setup systemd service (see EC2_DEPLOYMENT.md)"
else
    echo ""
    echo "=========================================="
    echo "❌ Health checks failed"
    echo "=========================================="
    echo ""
    echo "Check EC2_DEPLOYMENT.md for troubleshooting"
fi

exit $exit_code
