# HiveMind Deployment - Quick Start

## Prerequisites
- AWS CLI configured
- PowerShell 5.1+
- S3 bucket `media-ai-content` with Lambda packages

## One-Command Deployment

```powershell
cd deployment
.\deploy-all.ps1
```

## What Gets Deployed

1. **Lambda Layer** - Shared dependencies
2. **IAM Roles** - Lambda + Step Functions execution roles
3. **16 Lambda Functions** - All from S3
4. **API Gateway** - REST API with social endpoints
5. **Step Functions** - Video processing workflow

## Deployment Time

~5-10 minutes total

## Output Files

- `layer-arn.txt` - Lambda layer ARN
- `role-arn.txt` - Lambda execution role ARN
- `api-id.txt` - API Gateway ID
- `api-url.txt` - API Gateway endpoint URL
- `state-machine-arn.txt` - Step Functions ARN

## Post-Deployment

Update Lambda environment variables:

```powershell
# Get all function names
$functions = aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `hivemind-`)].FunctionName' --output text

# Update each function
foreach ($func in $functions -split '\s+') {
    aws lambda update-function-configuration `
        --function-name $func `
        --environment "Variables={
            DB_HOST=your-aurora-endpoint.rds.amazonaws.com,
            DB_PORT=5432,
            DB_NAME=hiveminddb,
            DB_USER=hivemind,
            DB_PASSWORD=your-password,
            S3_BUCKET=media-ai-content,
            AWS_REGION=ap-south-1
        }"
}
```

## Test API

```powershell
$API_URL = Get-Content api-url.txt
curl "$API_URL/social/brands"
```

## Test Step Functions

```powershell
$STATE_MACHINE_ARN = Get-Content state-machine-arn.txt

aws stepfunctions start-execution `
    --state-machine-arn $STATE_MACHINE_ARN `
    --input '{
        "videoId": "test-123",
        "s3Bucket": "media-ai-content",
        "s3Key": "videos/test.mp4"
    }'
```

## Cleanup

```powershell
.\cleanup.ps1
```

## Architecture

```
┌─────────────────────────────────────────┐
│         API Gateway (REST)              │
│  POST /social/brands                    │
│  GET  /social/brands                    │
│  GET  /social/brands/{id}               │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      Lambda Functions (16)              │
│  ┌────────────┐  ┌──────────────┐      │
│  │ API (9)    │  │ Step Fns (7) │      │
│  └────────────┘  └──────────────┘      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Lambda Layer                    │
│  boto3, psycopg2-binary                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         AWS Services                    │
│  S3 | Bedrock | Transcribe | Rekognition│
└─────────────────────────────────────────┘
```

## Troubleshooting

**IAM propagation error**: Wait 10 seconds and retry

**Function already exists**: Delete and redeploy
```powershell
aws lambda delete-function --function-name hivemind-social-create-brand
```

**API Gateway 500 error**: Check Lambda permissions
```powershell
aws lambda get-policy --function-name hivemind-social-create-brand
```
