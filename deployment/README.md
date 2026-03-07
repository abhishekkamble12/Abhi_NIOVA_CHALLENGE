# HiveMind Serverless Backend Deployment

Complete AWS infrastructure deployment for HiveMind AI Media OS.

## 📋 Prerequisites

- AWS CLI configured with credentials
- PowerShell 5.1+ (Windows) or Bash (Linux/macOS)
- S3 bucket `media-ai-content` with Lambda packages uploaded
- AWS Account: `586098609294`
- Region: `ap-south-1`

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway (REST)                       │
│  /social/brands (POST, GET)                                 │
│  /social/brands/{id} (GET)                                  │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│              Lambda Functions (16 total)                     │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  API Functions   │  │ Step Functions   │                │
│  │  - social_*      │  │ - validate_video │                │
│  │  - feed_*        │  │ - transcription  │                │
│  │  - ai_*          │  │ - rekognition    │                │
│  └──────────────────┘  └──────────────────┘                │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                  Lambda Layer (Shared)                       │
│  - boto3, psycopg2-binary                                   │
└─────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                   AWS Services                               │
│  - S3 (media storage)                                       │
│  - Bedrock (AI models)                                      │
│  - Transcribe (audio)                                       │
│  - Rekognition (video analysis)                             │
│  - DynamoDB (user activity)                                 │
│  - Aurora PostgreSQL (relational data)                      │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Deploy

### One-Command Deployment

```powershell
cd deployment
.\deploy-all.ps1
```

This runs all 5 deployment steps in order.

## 📝 Manual Deployment Steps

### Step 1: Deploy Lambda Layer

```bash
bash 1-deploy-layer.sh
```

**Output**: `layer-arn.txt`

**What it does**:
- Publishes Lambda layer from S3
- Creates `hivemind-shared-layer`
- Compatible with Python 3.11

### Step 2: Create IAM Role

```powershell
.\2-create-iam-role.ps1
```

**Output**: `role-arn.txt`

**What it does**:
- Creates `hivemind-lambda-execution-role`
- Attaches policies for:
  - CloudWatch Logs
  - S3 access
  - Bedrock invocation
  - Transcribe/Rekognition
  - DynamoDB access

### Step 3: Deploy Lambda Functions

```powershell
.\3-deploy-lambdas.ps1
```

**What it does**:
- Creates 16 Lambda functions from S3 ZIPs
- Attaches shared layer
- Sets environment variables (placeholders)
- Configures 512MB memory, 300s timeout

**Functions created**:
- `hivemind-social-create-brand`
- `hivemind-social-get-brand`
- `hivemind-social-list-brands`
- `hivemind-social-get-post`
- `hivemind-social-generate-content`
- `hivemind-feed-personalized`
- `hivemind-video-upload-handler`
- `hivemind-ai-generate-content`
- `hivemind-ai-process-video`
- `hivemind-stepfunctions-validate-video`
- `hivemind-stepfunctions-start-transcription`
- `hivemind-stepfunctions-check-transcription`
- `hivemind-stepfunctions-detect-scenes`
- `hivemind-stepfunctions-detect-labels`
- `hivemind-stepfunctions-check-rekognition`
- `hivemind-stepfunctions-store-video-results`

### Step 4: Create API Gateway

```powershell
.\4-create-api-gateway.ps1
```

**Output**: `api-url.txt`, `api-id.txt`

**What it does**:
- Creates REST API `HiveMind-API`
- Configures routes:
  - `POST /social/brands` → social_create_brand
  - `GET /social/brands` → social_list_brands
  - `GET /social/brands/{brand_id}` → social_get_brand
- Grants Lambda invoke permissions
- Deploys to `prod` stage

**API URL**: `https://{api-id}.execute-api.ap-south-1.amazonaws.com/prod`

### Step 5: Create Step Functions

```powershell
.\5-create-step-functions.ps1
```

**Output**: `state-machine-arn.txt`

**What it does**:
- Creates IAM role for Step Functions
- Deploys state machine `hivemind-video-processing`
- Configures parallel processing workflow

**Workflow**:
```
ValidateVideo
    ↓
ParallelProcessing
    ├─ Transcription (with polling)
    ├─ Scene Detection (with polling)
    └─ Label Detection (with polling)
    ↓
StoreResults
```

## 🔧 Post-Deployment Configuration

### Update Environment Variables

Replace placeholders with actual values:

```powershell
$functions = aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `hivemind-`)].FunctionName' --output text

foreach ($func in $functions -split '\s+') {
    aws lambda update-function-configuration `
        --function-name $func `
        --environment "Variables={
            DB_HOST=your-aurora-endpoint.rds.amazonaws.com,
            DB_PORT=5432,
            DB_NAME=hiveminddb,
            DB_USER=hivemind,
            DB_PASSWORD=your-secure-password,
            S3_BUCKET=media-ai-content,
            AWS_REGION=ap-south-1
        }"
}
```

### Enable Bedrock Model Access

```bash
# Via AWS Console:
# Bedrock → Model access → Request access
# Enable: Titan Embeddings, Claude 3 Sonnet
```

## 🧪 Testing

### Test API Gateway

```bash
# Get API URL
$API_URL = Get-Content api-url.txt

# Test list brands
curl "$API_URL/social/brands"

# Create brand
curl -X POST "$API_URL/social/brands" `
  -H "Content-Type: application/json" `
  -d '{"name":"TestBrand","industry":"Tech","tone":"professional","target_audience":"developers"}'
```

### Test Step Functions

```powershell
# Start execution
$STATE_MACHINE_ARN = Get-Content state-machine-arn.txt

aws stepfunctions start-execution `
    --state-machine-arn $STATE_MACHINE_ARN `
    --input '{
        "videoId": "test-video-123",
        "s3Bucket": "media-ai-content",
        "s3Key": "videos/test.mp4"
    }'

# Check execution status
aws stepfunctions list-executions `
    --state-machine-arn $STATE_MACHINE_ARN `
    --max-results 1
```

## 📊 Deployment Order

**Critical**: Follow this exact order to avoid dependency failures.

1. **Lambda Layer** - Must exist before functions
2. **IAM Role** - Required for Lambda execution
3. **Lambda Functions** - Depend on layer + role
4. **API Gateway** - Integrates with Lambda functions
5. **Step Functions** - Orchestrates Lambda functions

## 🔍 Verification

```powershell
# Check Lambda layer
aws lambda list-layer-versions --layer-name hivemind-shared-layer

# Check Lambda functions
aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `hivemind-`)].FunctionName'

# Check API Gateway
aws apigateway get-rest-apis --query 'items[?name==`HiveMind-API`]'

# Check Step Functions
aws stepfunctions list-state-machines --query 'stateMachines[?name==`hivemind-video-processing`]'
```

## 🗑️ Cleanup

```powershell
# Delete Step Functions
aws stepfunctions delete-state-machine --state-machine-arn $(Get-Content state-machine-arn.txt)

# Delete API Gateway
aws apigateway delete-rest-api --rest-api-id $(Get-Content api-id.txt)

# Delete Lambda functions
$functions = aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `hivemind-`)].FunctionName' --output text
foreach ($func in $functions -split '\s+') {
    aws lambda delete-function --function-name $func
}

# Delete Lambda layer
aws lambda delete-layer-version --layer-name hivemind-shared-layer --version-number 1

# Delete IAM roles
aws iam delete-role-policy --role-name hivemind-lambda-execution-role --policy-name hivemind-lambda-policy
aws iam detach-role-policy --role-name hivemind-lambda-execution-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name hivemind-lambda-execution-role
aws iam delete-role-policy --role-name hivemind-stepfunctions-role --policy-name StepFunctionsLambdaInvoke
aws iam delete-role --role-name hivemind-stepfunctions-role
```

## 💰 Cost Estimate

**Monthly costs (moderate usage)**:
- Lambda: $20-50 (1M requests)
- API Gateway: $10-30 (1M requests)
- Step Functions: $5-15 (10K executions)
- S3: $5-20 (storage + transfer)

**Total**: ~$40-115/month

## 🐛 Troubleshooting

### Lambda function creation fails

```
Error: Role not found
```

**Solution**: Wait 10 seconds after IAM role creation for propagation.

### API Gateway returns 500

```
Error: Execution failed due to configuration error
```

**Solution**: Check Lambda permissions:
```powershell
aws lambda get-policy --function-name hivemind-social-create-brand
```

### Step Functions execution fails

```
Error: Lambda invocation failed
```

**Solution**: Verify Step Functions role has Lambda invoke permissions.

## 📚 Additional Resources

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [API Gateway Developer Guide](https://docs.aws.amazon.com/apigateway/)
- [Step Functions Guide](https://docs.aws.amazon.com/step-functions/)
