# Next Steps - Complete Infrastructure Deployment

## ✅ Already Deployed

1. Lambda Layer
2. 16 Lambda Functions
3. API Gateway: https://wcp5c3ga8b.execute-api.ap-south-1.amazonaws.com/prod
4. Step Functions: arn:aws:states:ap-south-1:150809276128:stateMachine:hivemind-video-processing

## 🚀 What's Next

### 1. Create IAM Role for Lambda (REQUIRED)

```powershell
cd E:\Projects\HiveMind\aws\deployment

# Create the role
aws iam create-role `
    --role-name hivemind-lambda-execution-role `
    --assume-role-policy-document '{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"lambda.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}'

# Attach basic execution policy
aws iam attach-role-policy `
    --role-name hivemind-lambda-execution-role `
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Create custom policy file
@'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::media-ai-content/*"
    },
    {
      "Effect": "Allow",
      "Action": ["bedrock:InvokeModel"],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": ["transcribe:*", "rekognition:*"],
      "Resource": "*"
    }
  ]
}
'@ | Out-File -FilePath lambda-policy.json -Encoding utf8

# Attach custom policy
aws iam put-role-policy `
    --role-name hivemind-lambda-execution-role `
    --policy-name hivemind-lambda-policy `
    --policy-document file://lambda-policy.json

# Get role ARN
$ROLE_ARN = aws iam get-role --role-name hivemind-lambda-execution-role --query 'Role.Arn' --output text
Write-Host "Role ARN: $ROLE_ARN"
$ROLE_ARN | Out-File role-arn.txt
```

### 2. Update Lambda Functions with IAM Role

```powershell
$ROLE_ARN = Get-Content role-arn.txt

# Wait for IAM propagation
Start-Sleep -Seconds 15

# Update all functions
$functions = @(
    "hivemind-social-create-brand",
    "hivemind-social-get-brand",
    "hivemind-social-list-brands",
    "hivemind-social-get-post",
    "hivemind-social-generate-content",
    "hivemind-feed-personalized",
    "hivemind-video-upload-handler",
    "hivemind-ai-generate-content",
    "hivemind-ai-process-video",
    "hivemind-stepfunctions-validate-video",
    "hivemind-stepfunctions-start-transcription",
    "hivemind-stepfunctions-check-transcription",
    "hivemind-stepfunctions-detect-scenes",
    "hivemind-stepfunctions-detect-labels",
    "hivemind-stepfunctions-check-rekognition",
    "hivemind-stepfunctions-store-video-results"
)

foreach ($func in $functions) {
    Write-Host "Updating $func..."
    aws lambda update-function-configuration `
        --function-name $func `
        --role $ROLE_ARN `
        --region ap-south-1
    Start-Sleep -Seconds 2
}
```

### 3. Grant API Gateway Permission to Invoke Lambda

```powershell
$API_ID = "wcp5c3ga8b"
$ACCOUNT_ID = "150809276128"
$REGION = "ap-south-1"

# Grant permissions for API Gateway functions
aws lambda add-permission `
    --function-name hivemind-social-create-brand `
    --statement-id apigateway-invoke-1 `
    --action lambda:InvokeFunction `
    --principal apigateway.amazonaws.com `
    --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/*"

aws lambda add-permission `
    --function-name hivemind-social-list-brands `
    --statement-id apigateway-invoke-2 `
    --action lambda:InvokeFunction `
    --principal apigateway.amazonaws.com `
    --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/*"

aws lambda add-permission `
    --function-name hivemind-social-get-brand `
    --statement-id apigateway-invoke-3 `
    --action lambda:InvokeFunction `
    --principal apigateway.amazonaws.com `
    --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/*"
```

### 4. Deploy Database Infrastructure

```powershell
# Create Aurora PostgreSQL cluster
cd E:\Projects\HiveMind\aws\backend-aws

# Deploy storage stack (Aurora + DynamoDB + S3)
sam deploy `
    --template-file template-storage.yaml `
    --stack-name hivemind-storage `
    --capabilities CAPABILITY_IAM `
    --region ap-south-1 `
    --parameter-overrides `
        VpcId=<YOUR_VPC_ID> `
        SubnetIds=<SUBNET_1>,<SUBNET_2> `
        DBUsername=hivemind `
        DBPassword=<STRONG_PASSWORD>
```

### 5. Update Lambda Environment Variables

```powershell
# After Aurora is deployed, get endpoint
$AURORA_ENDPOINT = aws cloudformation describe-stacks `
    --stack-name hivemind-storage `
    --query 'Stacks[0].Outputs[?OutputKey==`AuroraEndpoint`].OutputValue' `
    --output text

# Update all Lambda functions
$functions = aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `hivemind-`)].FunctionName' --output text

foreach ($func in $functions -split '\s+') {
    aws lambda update-function-configuration `
        --function-name $func `
        --environment "Variables={
            DB_HOST=$AURORA_ENDPOINT,
            DB_PORT=5432,
            DB_NAME=hiveminddb,
            DB_USER=hivemind,
            DB_PASSWORD=<YOUR_PASSWORD>,
            S3_BUCKET=media-ai-content,
            AWS_REGION=ap-south-1
        }"
}
```

### 6. Test API Gateway

```powershell
$API_URL = "https://wcp5c3ga8b.execute-api.ap-south-1.amazonaws.com/prod"

# Test list brands
curl "$API_URL/social/brands"

# Create test brand
curl -X POST "$API_URL/social/brands" `
    -H "Content-Type: application/json" `
    -d '{\"name\":\"TestBrand\",\"industry\":\"Tech\",\"tone\":\"professional\",\"target_audience\":\"developers\"}'
```

### 7. Test Step Functions

```powershell
$STATE_MACHINE_ARN = "arn:aws:states:ap-south-1:150809276128:stateMachine:hivemind-video-processing"

# Start execution
aws stepfunctions start-execution `
    --state-machine-arn $STATE_MACHINE_ARN `
    --input '{\"videoId\":\"test-123\",\"s3Bucket\":\"media-ai-content\",\"s3Key\":\"videos/test.mp4\"}'

# Check status
aws stepfunctions list-executions `
    --state-machine-arn $STATE_MACHINE_ARN `
    --max-results 1
```

## 📋 Deployment Checklist

- [x] S3 Bucket created
- [x] Lambda Layer deployed
- [x] Lambda Functions created
- [x] API Gateway created
- [x] Step Functions created
- [ ] IAM Role for Lambda
- [ ] Lambda functions updated with IAM role
- [ ] API Gateway permissions granted
- [ ] Aurora PostgreSQL deployed
- [ ] DynamoDB tables created
- [ ] Lambda environment variables configured
- [ ] API tested
- [ ] Step Functions tested

## 🔧 Quick Fix Commands

### If Lambda functions fail (missing role):
```powershell
# Create role first, then update functions
.\update-lambda-roles.ps1
```

### If API Gateway returns 500:
```powershell
# Grant invoke permissions
.\grant-api-permissions.ps1
```

### If database connection fails:
```powershell
# Check security groups allow Lambda access
aws ec2 describe-security-groups --group-ids <sg-id>
```

## 📊 Current Architecture

```
✅ API Gateway → ⚠️ Lambda Functions (need IAM role) → ❌ Databases (not deployed)
✅ Step Functions → ⚠️ Lambda Functions (need IAM role)
```

## 🎯 Priority Actions

1. **Create IAM role** (5 minutes)
2. **Update Lambda functions** (5 minutes)
3. **Grant API permissions** (2 minutes)
4. **Test API** (1 minute)

Total time: ~15 minutes to working API
