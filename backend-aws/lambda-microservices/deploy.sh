#!/bin/bash
# Deploy Lambda Microservices

set -e

echo "=========================================="
echo "🚀 Deploying Lambda Microservices"
echo "=========================================="

# Build Lambda layer
echo "📦 Building Lambda layer..."
mkdir -p layer/python
pip install -r requirements.txt -t layer/python/
cp -r services layer/python/
cp -r shared layer/python/
cp -r ../services layer/python/

echo "✅ Layer built"

# Build with SAM
echo "🔨 Building with SAM..."
sam build

echo "✅ Build complete"

# Deploy
echo "🚀 Deploying to AWS..."
sam deploy \
  --stack-name hivemind-lambda \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    DBUsername=postgres \
    DBPassword=$DB_PASSWORD \
    VpcId=$VPC_ID \
    SubnetIds=$SUBNET_IDS

echo ""
echo "=========================================="
echo "✅ Deployment Complete"
echo "=========================================="
echo ""
echo "Get API URL:"
echo "  aws cloudformation describe-stacks \\"
echo "    --stack-name hivemind-lambda \\"
echo "    --query 'Stacks[0].Outputs[?OutputKey==\`ApiUrl\`].OutputValue' \\"
echo "    --output text"
echo ""
echo "=========================================="
