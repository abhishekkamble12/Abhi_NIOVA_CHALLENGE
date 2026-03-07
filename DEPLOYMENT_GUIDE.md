# HiveMind AWS Deployment Guide

**Complete step-by-step deployment workflow for AWS cloud-native architecture**

---

## Prerequisites

- AWS Account with admin access
- AWS CLI v2 installed and configured
- SAM CLI installed (`pip install aws-sam-cli`)
- Node.js 18+ and npm
- Python 3.11
- PostgreSQL client (psql)

```bash
# Verify installations
aws --version
sam --version
node --version
python --version
```

---

## Architecture Overview

**Frontend**: Next.js → S3 → CloudFront  
**Backend**: API Gateway → Lambda (Python 3.11)  
**Storage**: Aurora PostgreSQL + DynamoDB + S3 + OpenSearch  
**AI**: Bedrock + Transcribe + Rekognition  
**Events**: EventBridge + Step Functions

**Region**: ap-south-1 (Mumbai)

---

## Deployment Checklist

### Phase 1: Core Infrastructure
- [ ] 1.1 Create VPC and networking
- [ ] 1.2 Deploy Aurora PostgreSQL cluster
- [ ] 1.3 Apply database schema
- [ ] 1.4 Create S3 media bucket
- [ ] 1.5 Deploy DynamoDB tables
- [ ] 1.6 Deploy OpenSearch domain

### Phase 2: Lambda & API Gateway
- [ ] 2.1 Package Lambda dependencies
- [ ] 2.2 Create Lambda layer
- [ ] 2.3 Deploy Lambda functions
- [ ] 2.4 Deploy API Gateway
- [ ] 2.5 Test API endpoints

### Phase 3: Event Pipeline
- [ ] 3.1 Create EventBridge bus
- [ ] 3.2 Deploy Step Functions
- [ ] 3.3 Configure S3 event notifications
- [ ] 3.4 Test video processing pipeline

### Phase 4: AI Services
- [ ] 4.1 Enable Bedrock model access
- [ ] 4.2 Configure IAM permissions
- [ ] 4.3 Test AI integrations

### Phase 5: Frontend
- [ ] 5.1 Build Next.js application
- [ ] 5.2 Deploy to S3
- [ ] 5.3 Create CloudFront distribution
- [ ] 5.4 Configure DNS (optional)

---

## Phase 1: Core Infrastructure

### 1.1 Create VPC and Networking

```bash
# Create VPC with public and private subnets
aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=hivemind-vpc}]' \
  --region ap-south-1

# Save VPC ID
export VPC_ID=<vpc-id-from-output>

# Create private subnets (2 AZs for Aurora/OpenSearch)
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone ap-south-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=hivemind-private-1a}]'

aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone ap-south-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=hivemind-private-1b}]'

# Save subnet IDs
export SUBNET_1=<subnet-1-id>
export SUBNET_2=<subnet-2-id>
```

### 1.2 Deploy Aurora PostgreSQL Cluster

```bash
cd backend-aws

# Deploy storage stack (includes Aurora)
sam deploy \
  --template-file template-storage.yaml \
  --stack-name hivemind-storage \
  --parameter-overrides \
    VpcId=$VPC_ID \
    SubnetIds=$SUBNET_1,$SUBNET_2 \
    DBUsername=hivemind \
    DBPassword=<STRONG_PASSWORD> \
  --capabilities CAPABILITY_IAM \
  --region ap-south-1

# Get Aurora endpoint
export AURORA_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name hivemind-storage \
  --query 'Stacks[0].Outputs[?OutputKey==`AuroraEndpoint`].OutputValue' \
  --output text \
  --region ap-south-1)

echo "Aurora Endpoint: $AURORA_ENDPOINT"
```

### 1.3 Apply Database Schema

```bash
# Connect to Aurora and apply schema
psql -h $AURORA_ENDPOINT \
  -U hivemind \
  -d hiveminddb \
  -f schema-aurora.sql

# Verify tables created
psql -h $AURORA_ENDPOINT -U hivemind -d hiveminddb -c "\dt"
```

**Expected output**: 8 tables (brands, social_posts, engagement, videos, articles, user_preferences, performance_analytics)

### 1.4 Create S3 Media Bucket

```bash
# Deploy S3 with EventBridge
sam deploy \
  --template-file template-s3-eventbridge.yaml \
  --stack-name hivemind-s3-events \
  --parameter-overrides EventBusName=hivemind-bus \
  --capabilities CAPABILITY_IAM \
  --region ap-south-1

# Get bucket name
export S3_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name hivemind-s3-events \
  --query 'Stacks[0].Outputs[?OutputKey==`MediaBucketName`].OutputValue' \
  --output text \
  --region ap-south-1)

echo "S3 Bucket: $S3_BUCKET"
```

### 1.5 Deploy DynamoDB Tables

DynamoDB tables are created by `template-storage.yaml` in step 1.2.

Verify:
```bash
aws dynamodb list-tables --region ap-south-1
```

**Expected**: `hivemind-activity`, `hivemind-sessions`

### 1.6 Deploy OpenSearch Domain

```bash
# Deploy OpenSearch in VPC
sam deploy \
  --template-file template-opensearch-vpc.yaml \
  --stack-name hivemind-opensearch \
  --parameter-overrides \
    VpcId=$VPC_ID \
    SubnetIds=$SUBNET_1,$SUBNET_2 \
  --capabilities CAPABILITY_IAM \
  --region ap-south-1

# Get OpenSearch endpoint (takes 15-20 minutes)
export OPENSEARCH_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name hivemind-opensearch \
  --query 'Stacks[0].Outputs[?OutputKey==`OpenSearchDomainEndpoint`].OutputValue' \
  --output text \
  --region ap-south-1)

echo "OpenSearch Endpoint: $OPENSEARCH_ENDPOINT"
```

---

## Phase 2: Lambda & API Gateway

### 2.1 Package Lambda Dependencies

```bash
cd backend-aws/lambda-microservices

# Create layer directory
mkdir -p layers/python

# Install dependencies for Lambda layer
pip install -r layers/requirements.txt -t layers/python/

# Install psycopg2-binary for database access
pip install psycopg2-binary -t layers/python/
```

### 2.2 Create Lambda Layer

```bash
# Package layer
cd layers
zip -r lambda-layer.zip python/

# Upload to S3
aws s3 cp lambda-layer.zip s3://$S3_BUCKET/layers/lambda-layer.zip

# Publish layer
aws lambda publish-layer-version \
  --layer-name hivemind-shared-layer \
  --content S3Bucket=$S3_BUCKET,S3Key=layers/lambda-layer.zip \
  --compatible-runtimes python3.11 \
  --region ap-south-1

# Save layer ARN
export LAYER_ARN=$(aws lambda list-layer-versions \
  --layer-name hivemind-shared-layer \
  --query 'LayerVersions[0].LayerVersionArn' \
  --output text \
  --region ap-south-1)
```

### 2.3 Deploy Lambda Functions

```bash
cd backend-aws

# Package Lambda code
sam build --template-file template-api-gateway.yaml

# Deploy API Gateway + Lambda functions
sam deploy \
  --template-file template-api-gateway.yaml \
  --stack-name hivemind-api \
  --parameter-overrides Environment=prod \
  --capabilities CAPABILITY_IAM \
  --region ap-south-1
```

### 2.4 Configure Lambda Environment Variables

```bash
# Get Lambda function names
aws lambda list-functions \
  --query 'Functions[?starts_with(FunctionName, `hivemind-`)].FunctionName' \
  --output text \
  --region ap-south-1

# Update environment variables for all Lambda functions
for FUNCTION in $(aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `hivemind-`)].FunctionName' --output text --region ap-south-1); do
  aws lambda update-function-configuration \
    --function-name $FUNCTION \
    --environment "Variables={
      DB_HOST=$AURORA_ENDPOINT,
      DB_PORT=5432,
      DB_NAME=hiveminddb,
      DB_USER=hivemind,
      DB_PASSWORD=<YOUR_DB_PASSWORD>,
      S3_BUCKET=$S3_BUCKET,
      OPENSEARCH_ENDPOINT=$OPENSEARCH_ENDPOINT,
      AWS_REGION=ap-south-1
    }" \
    --region ap-south-1
done
```

### 2.5 Get API Gateway URL

```bash
export API_URL=$(aws cloudformation describe-stacks \
  --stack-name hivemind-api \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text \
  --region ap-south-1)

echo "API Gateway URL: $API_URL"
```

### 2.6 Test API Endpoints

```bash
# Test health check
curl $API_URL/social/brands

# Create test brand
curl -X POST $API_URL/social/brands \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Brand",
    "industry": "Technology",
    "tone": "professional",
    "target_audience": "developers"
  }'
```

---

## Phase 3: Event Pipeline

### 3.1 Create EventBridge Bus

EventBridge bus is created by `template-s3-eventbridge.yaml` in Phase 1.

Verify:
```bash
aws events list-event-buses --region ap-south-1
```

### 3.2 Deploy Step Functions Lambdas

```bash
cd backend-aws/lambda-microservices

# Package Step Functions Lambda handlers
zip -r stepfunctions-lambdas.zip handlers/stepfunctions_*.py services/

# Upload to S3
aws s3 cp stepfunctions-lambdas.zip s3://$S3_BUCKET/lambda/stepfunctions-lambdas.zip

# Create Lambda functions for Step Functions
FUNCTIONS=(
  "validate-video"
  "start-transcription"
  "check-transcription"
  "detect-scenes"
  "detect-labels"
  "check-rekognition"
  "store-video-results"
)

for FUNC in "${FUNCTIONS[@]}"; do
  aws lambda create-function \
    --function-name hivemind-$FUNC \
    --runtime python3.11 \
    --role <LAMBDA_ROLE_ARN> \
    --handler handlers.stepfunctions_${FUNC//-/_}.handler \
    --code S3Bucket=$S3_BUCKET,S3Key=lambda/stepfunctions-lambdas.zip \
    --timeout 300 \
    --memory-size 512 \
    --layers $LAYER_ARN \
    --environment "Variables={
      DB_HOST=$AURORA_ENDPOINT,
      DB_PASSWORD=<YOUR_DB_PASSWORD>,
      S3_BUCKET=$S3_BUCKET,
      AWS_REGION=ap-south-1
    }" \
    --region ap-south-1
done
```

### 3.3 Verify Step Functions State Machine

```bash
# Get state machine ARN
aws stepfunctions list-state-machines \
  --query 'stateMachines[?name==`hivemind-video-processing`].stateMachineArn' \
  --output text \
  --region ap-south-1
```

### 3.4 Test Video Processing Pipeline

```bash
# Upload test video to S3
aws s3 cp test-video.mp4 s3://$S3_BUCKET/videos/test-video.mp4

# Check Step Functions execution
aws stepfunctions list-executions \
  --state-machine-arn <STATE_MACHINE_ARN> \
  --region ap-south-1

# View execution details
aws stepfunctions describe-execution \
  --execution-arn <EXECUTION_ARN> \
  --region ap-south-1
```

---

## Phase 4: AI Services

### 4.1 Enable Bedrock Model Access

```bash
# Request access to Bedrock models (via AWS Console)
# Navigate to: Bedrock → Model access → Request access
# Enable:
# - Amazon Titan Embeddings G1 - Text
# - Anthropic Claude 3 Sonnet
# - Anthropic Claude 3 Haiku

# Verify access
aws bedrock list-foundation-models \
  --region ap-south-1 \
  --query 'modelSummaries[?modelId==`amazon.titan-embed-text-v1`]'
```

### 4.2 Configure IAM Permissions

IAM permissions are configured in CloudFormation templates. Verify:

```bash
# Check Lambda execution role has Bedrock permissions
aws iam get-role-policy \
  --role-name <LAMBDA_ROLE_NAME> \
  --policy-name BedrockPolicy \
  --region ap-south-1
```

### 4.3 Test AI Integrations

```bash
# Test Bedrock content generation
curl -X POST $API_URL/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Generate a LinkedIn post about AI innovation",
    "platform": "linkedin"
  }'

# Test social content generation
curl -X POST $API_URL/social/generate/content \
  -H "Content-Type: application/json" \
  -d '{
    "brand_id": "<BRAND_ID>",
    "platform": "instagram",
    "topic": "product launch"
  }'
```

---

## Phase 5: Frontend Deployment

### 5.1 Build Next.js Application

```bash
cd aws  # Root directory with Next.js app

# Set production API URL
echo "NEXT_PUBLIC_API_URL=$API_URL" > .env.production

# Install dependencies
npm install

# Build for production
npm run build

# Export static files
npx next export
```

### 5.2 Create S3 Bucket for Frontend

```bash
# Create frontend bucket
aws s3 mb s3://hivemind-frontend-$AWS_ACCOUNT_ID --region ap-south-1

# Enable static website hosting
aws s3 website s3://hivemind-frontend-$AWS_ACCOUNT_ID \
  --index-document index.html \
  --error-document 404.html

# Upload build files
aws s3 sync out/ s3://hivemind-frontend-$AWS_ACCOUNT_ID/ \
  --delete \
  --cache-control "public, max-age=31536000, immutable"
```

### 5.3 Create CloudFront Distribution

```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name hivemind-frontend-$AWS_ACCOUNT_ID.s3.ap-south-1.amazonaws.com \
  --default-root-object index.html \
  --region ap-south-1

# Get CloudFront domain
aws cloudfront list-distributions \
  --query 'DistributionList.Items[0].DomainName' \
  --output text
```

**CloudFront Configuration (via Console)**:
1. Origin: S3 bucket
2. Viewer Protocol Policy: Redirect HTTP to HTTPS
3. Allowed HTTP Methods: GET, HEAD, OPTIONS
4. Cache Policy: CachingOptimized
5. Custom Error Response: 404 → /index.html (for SPA routing)

### 5.4 Configure DNS (Optional)

```bash
# If using Route 53
aws route53 create-hosted-zone --name yourdomain.com

# Create A record pointing to CloudFront
aws route53 change-resource-record-sets \
  --hosted-zone-id <ZONE_ID> \
  --change-batch file://dns-record.json
```

---

## Phase 6: Post-Deployment Validation

### 6.1 API Health Checks

```bash
# Test all API endpoints
echo "Testing Social API..."
curl $API_URL/social/brands

echo "Testing Feed API..."
curl $API_URL/feed/real/personalized/test-user-123

echo "Testing AI API..."
curl -X POST $API_URL/ai/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test", "platform": "linkedin"}'
```

### 6.2 Event Pipeline Test

```bash
# Upload video and verify processing
aws s3 cp test-video.mp4 s3://$S3_BUCKET/videos/test-$(date +%s).mp4

# Check Step Functions execution
aws stepfunctions list-executions \
  --state-machine-arn <STATE_MACHINE_ARN> \
  --max-results 1 \
  --region ap-south-1

# Check CloudWatch Logs
aws logs tail /aws/lambda/hivemind-validate-video --follow
```

### 6.3 Database Connectivity Test

```bash
# Connect to Aurora
psql -h $AURORA_ENDPOINT -U hivemind -d hiveminddb

# Run test queries
SELECT COUNT(*) FROM brands;
SELECT COUNT(*) FROM social_posts;
SELECT COUNT(*) FROM videos;
```

### 6.4 AI Service Test

```bash
# Test Bedrock embeddings
aws bedrock-runtime invoke-model \
  --model-id amazon.titan-embed-text-v1 \
  --body '{"inputText":"test embedding"}' \
  --region ap-south-1 \
  output.json

# Test Transcribe
aws transcribe start-transcription-job \
  --transcription-job-name test-job-$(date +%s) \
  --media MediaFileUri=s3://$S3_BUCKET/videos/test-video.mp4 \
  --language-code en-US \
  --region ap-south-1
```

---

## Environment Variables Summary

**Lambda Functions**:
```bash
DB_HOST=<aurora-endpoint>
DB_PORT=5432
DB_NAME=hiveminddb
DB_USER=hivemind
DB_PASSWORD=<password>
S3_BUCKET=<media-bucket-name>
OPENSEARCH_ENDPOINT=<opensearch-endpoint>
AWS_REGION=ap-south-1
```

**Frontend (.env.production)**:
```bash
NEXT_PUBLIC_API_URL=<api-gateway-url>
```

---

## Cost Estimates

**Monthly costs (moderate usage)**:
- Aurora Serverless v2: $50-100
- Lambda: $20-50
- API Gateway: $10-30
- S3: $5-20
- DynamoDB: $5-15
- OpenSearch: $80-150
- Bedrock: Pay per use (~$50-200)
- CloudFront: $10-30

**Total**: ~$230-595/month

---

## Troubleshooting

### Lambda timeout errors
```bash
# Increase timeout
aws lambda update-function-configuration \
  --function-name <function-name> \
  --timeout 300
```

### Database connection errors
```bash
# Check security group allows Lambda access
aws ec2 describe-security-groups --group-ids <sg-id>

# Verify Lambda in same VPC
aws lambda get-function-configuration --function-name <function-name>
```

### API Gateway CORS errors
```bash
# Verify CORS headers in Lambda response
# Must include: Access-Control-Allow-Origin: *
```

### Step Functions failures
```bash
# View execution history
aws stepfunctions get-execution-history \
  --execution-arn <execution-arn> \
  --region ap-south-1
```

---

## Cleanup (Destroy All Resources)

```bash
# Delete CloudFormation stacks
aws cloudformation delete-stack --stack-name hivemind-api
aws cloudformation delete-stack --stack-name hivemind-s3-events
aws cloudformation delete-stack --stack-name hivemind-opensearch
aws cloudformation delete-stack --stack-name hivemind-storage

# Empty and delete S3 buckets
aws s3 rm s3://$S3_BUCKET --recursive
aws s3 rb s3://$S3_BUCKET

# Delete CloudFront distribution (must disable first)
aws cloudfront delete-distribution --id <distribution-id>
```

---

## Next Steps

1. **Monitoring**: Set up CloudWatch dashboards
2. **Alerts**: Configure SNS notifications for errors
3. **CI/CD**: Implement GitHub Actions deployment pipeline
4. **Security**: Enable AWS WAF on API Gateway
5. **Backup**: Configure Aurora automated backups
6. **Scaling**: Adjust Aurora/OpenSearch capacity based on load

---

**Deployment Complete! 🚀**

Frontend: `https://<cloudfront-domain>`  
API: `$API_URL`
