#!/bin/bash

set -e

echo "=========================================="
echo "🚀 HiveMind AWS Backend Startup"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please configure .env with your AWS credentials${NC}"
    exit 1
fi

# Load environment variables
export $(grep -v '^#' .env | xargs)

echo -e "${GREEN}✅ Environment variables loaded${NC}"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION detected${NC}"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Verify AWS credentials
echo "Verifying AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi

AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
echo -e "${GREEN}✅ AWS Account: $AWS_ACCOUNT${NC}"

# Test Aurora connection
echo "Testing Aurora PostgreSQL connection..."
python3 -c "
import asyncio
from services.aurora_service import get_db_session

async def test():
    try:
        async with get_db_session() as db:
            result = await db.execute('SELECT 1')
            print('✅ Aurora connected')
    except Exception as e:
        print(f'❌ Aurora connection failed: {e}')
        exit(1)

asyncio.run(test())
" || echo -e "${YELLOW}⚠️  Aurora not available (optional for local dev)${NC}"

# Test ElastiCache connection
echo "Testing ElastiCache Redis connection..."
python3 -c "
import asyncio
from services.cache_service import get_cache_service

async def test():
    try:
        cache = get_cache_service()
        await cache.set('test', 'ok', ttl=10)
        result = await cache.get('test')
        print('✅ ElastiCache connected')
    except Exception as e:
        print(f'❌ ElastiCache connection failed: {e}')
        exit(1)

asyncio.run(test())
" || echo -e "${YELLOW}⚠️  ElastiCache not available (optional for local dev)${NC}"

# Test S3 access
echo "Testing S3 access..."
aws s3 ls s3://$S3_BUCKET &> /dev/null && echo -e "${GREEN}✅ S3 bucket accessible${NC}" || echo -e "${YELLOW}⚠️  S3 bucket not accessible${NC}"

# Test Bedrock access
echo "Testing Bedrock access..."
aws bedrock list-foundation-models --region $BEDROCK_REGION &> /dev/null && echo -e "${GREEN}✅ Bedrock accessible${NC}" || echo -e "${YELLOW}⚠️  Bedrock not accessible${NC}"

# Run example usage
echo ""
echo "=========================================="
echo "🧪 Running Example Workflows"
echo "=========================================="

python3 example_usage.py

echo ""
echo "=========================================="
echo "✅ HiveMind AWS Backend Started"
echo "=========================================="
echo ""
echo "Services Status:"
echo "  • Aurora PostgreSQL: $DB_CLUSTER_ARN"
echo "  • ElastiCache Redis: $REDIS_ENDPOINT"
echo "  • S3 Bucket: s3://$S3_BUCKET"
echo "  • EventBridge Bus: $EVENT_BUS_NAME"
echo "  • Bedrock Region: $BEDROCK_REGION"
echo ""
echo "Next Steps:"
echo "  1. Deploy Lambda functions: ./deploy_lambda.sh"
echo "  2. Create EventBridge rules: ./deploy_events.sh"
echo "  3. Deploy Step Functions: ./deploy_stepfunctions.sh"
echo ""
echo "=========================================="
