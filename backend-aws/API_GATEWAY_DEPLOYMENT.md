# API Gateway Integration - Deployment Guide

## Overview

This corrected CloudFormation template connects all Lambda microservices to API Gateway with proper routing, CORS, and permissions.

## Architecture

```
API Gateway (REST API)
├── /social/brands
│   ├── POST → SocialCreateBrandFunction
│   └── GET → SocialListBrandsFunction
├── /social/brands/{brand_id}
│   └── GET → SocialGetBrandFunction
├── /social/generate/content
│   └── POST → SocialGenerateContentFunction
├── /social/posts/{post_id}
│   └── GET → SocialGetPostFunction
├── /feed/real/personalized/{userId}
│   └── GET → FeedPersonalizedFunction
├── /videos/videos/upload
│   └── POST → VideoUploadFunction
├── /ai/generate
│   └── POST → AIGenerateContentFunction
└── /ai/video/process
    └── POST → AIProcessVideoFunction
```

## Key Features

### ✅ API Gateway Proxy Integration
All Lambda functions use `AWS_PROXY` integration automatically via SAM `Api` event source.

### ✅ CORS Enabled
Global CORS configuration:
```yaml
Cors:
  AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
  AllowHeaders: "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
  AllowOrigin: "'*'"
```

### ✅ Path Parameters Mapped
- `/social/brands/{brand_id}` → `event['pathParameters']['brand_id']`
- `/feed/real/personalized/{userId}` → `event['pathParameters']['userId']`
- `/social/posts/{post_id}` → `event['pathParameters']['post_id']`

### ✅ Lambda Permissions
SAM automatically creates `AWS::Lambda::Permission` resources for API Gateway invocation.

### ✅ IAM Policies
Specific permissions for each function:
- **Bedrock**: `bedrock:InvokeModel` for AI functions
- **S3**: `s3:PutObject`, `s3:GetObject` for video upload
- **Transcribe**: `transcribe:StartTranscriptionJob` for video processing
- **Rekognition**: `rekognition:Start*Detection` for video analysis

## Deployment

### Prerequisites
```bash
# Install AWS SAM CLI
pip install aws-sam-cli

# Configure AWS credentials
aws configure
```

### Deploy Stack
```bash
cd backend-aws

# Build
sam build -t template-api-gateway.yaml

# Deploy (first time)
sam deploy --guided \
  --template-file template-api-gateway.yaml \
  --stack-name hivemind-api \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides Environment=prod

# Deploy (subsequent)
sam deploy --template-file template-api-gateway.yaml
```

### Deployment Parameters
- **Environment**: `dev`, `staging`, or `prod` (default: `prod`)

## Testing

### Get API URL
```bash
aws cloudformation describe-stacks \
  --stack-name hivemind-api \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text
```

### Test Endpoints

#### Create Brand
```bash
curl -X POST https://{api-id}.execute-api.ap-south-1.amazonaws.com/prod/social/brands \
  -H "Content-Type: application/json" \
  -d '{
    "name": "TechCorp",
    "industry": "technology",
    "tone": "professional",
    "target_audience": "developers"
  }'
```

#### Get Brand
```bash
curl https://{api-id}.execute-api.ap-south-1.amazonaws.com/prod/social/brands/1
```

#### Generate Content
```bash
curl -X POST "https://{api-id}.execute-api.ap-south-1.amazonaws.com/prod/social/generate/content?brand_id=1&platform=instagram"
```

#### Get Personalized Feed
```bash
curl "https://{api-id}.execute-api.ap-south-1.amazonaws.com/prod/feed/real/personalized/user-123?limit=10"
```

#### Upload Video
```bash
curl -X POST https://{api-id}.execute-api.ap-south-1.amazonaws.com/prod/videos/videos/upload \
  -F "file=@video.mp4"
```

## Frontend Integration

### Update Next.js API Client

**File**: `app/lib/api.ts`

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
  'https://{api-id}.execute-api.ap-south-1.amazonaws.com/prod';

export const apiClient = {
  brand: {
    create: async (brandData: any) => {
      const res = await fetch(`${API_BASE_URL}/social/brands`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(brandData),
      });
      return res.json();
    },
    
    get: async (brandId: number) => {
      const res = await fetch(`${API_BASE_URL}/social/brands/${brandId}`);
      return res.json();
    },
  },
  
  content: {
    generate: async (brandId: number, platform: string) => {
      const res = await fetch(
        `${API_BASE_URL}/social/generate/content?brand_id=${brandId}&platform=${platform}`,
        { method: 'POST' }
      );
      return res.json();
    },
  },
  
  feed: {
    getPersonalizedFeed: async (userId: number, limit: number = 20) => {
      const res = await fetch(
        `${API_BASE_URL}/feed/real/personalized/${userId}?limit=${limit}`
      );
      return res.json();
    },
  },
  
  videos: {
    upload: async (formData: FormData) => {
      const res = await fetch(`${API_BASE_URL}/videos/videos/upload`, {
        method: 'POST',
        body: formData,
      });
      return res.json();
    },
  },
};
```

### Environment Variables

**File**: `.env.local`
```bash
NEXT_PUBLIC_API_URL=https://{api-id}.execute-api.ap-south-1.amazonaws.com/prod
```

## Monitoring

### CloudWatch Logs
```bash
# View Lambda logs
sam logs -n SocialCreateBrandFunction --stack-name hivemind-api --tail

# View API Gateway logs
aws logs tail /aws/apigateway/hivemind-api --follow
```

### API Gateway Metrics
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --dimensions Name=ApiName,Value=HiveMindAPI \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum
```

## Troubleshooting

### Issue: 403 Forbidden
**Cause**: Lambda permission missing  
**Fix**: SAM automatically creates permissions. Redeploy stack.

### Issue: 502 Bad Gateway
**Cause**: Lambda function error  
**Fix**: Check CloudWatch logs:
```bash
sam logs -n {FunctionName} --stack-name hivemind-api --tail
```

### Issue: CORS Error
**Cause**: Missing CORS headers in Lambda response  
**Fix**: Ensure all Lambda responses include:
```python
{
    'statusCode': 200,
    'headers': {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    },
    'body': json.dumps(data)
}
```

### Issue: Path Parameter Not Found
**Cause**: Incorrect path parameter extraction  
**Fix**: Use correct syntax:
```python
brand_id = event.get('pathParameters', {}).get('brand_id')
```

## Cost Estimate

| Resource | Usage | Monthly Cost |
|----------|-------|--------------|
| API Gateway | 1M requests | $3.50 |
| Lambda | 1M invocations (512MB, 1s avg) | $10.00 |
| CloudWatch Logs | 10GB | $5.00 |
| **Total** | | **~$18.50/month** |

## Next Steps

1. ✅ Deploy API Gateway stack
2. ✅ Update frontend API URL
3. ⚠️ Add authentication (Cognito)
4. ⚠️ Implement rate limiting
5. ⚠️ Add custom domain
6. ⚠️ Enable API Gateway caching
7. ⚠️ Set up CloudWatch alarms

## Security Recommendations

### Add API Key
```yaml
HiveMindApi:
  Type: AWS::Serverless::Api
  Properties:
    Auth:
      ApiKeyRequired: true
```

### Add Cognito Authorizer
```yaml
HiveMindApi:
  Type: AWS::Serverless::Api
  Properties:
    Auth:
      DefaultAuthorizer: CognitoAuthorizer
      Authorizers:
        CognitoAuthorizer:
          UserPoolArn: !GetAtt UserPool.Arn
```

### Enable WAF
```bash
aws wafv2 associate-web-acl \
  --web-acl-arn {waf-acl-arn} \
  --resource-arn {api-gateway-arn}
```

## Differences from Original Template

### Before (Hivemind-stack.yaml)
- ❌ Only 1 route: `/generate`
- ❌ Inline Lambda code
- ❌ No CORS configuration
- ❌ Manual permission management

### After (template-api-gateway.yaml)
- ✅ 8 routes covering all features
- ✅ Proper Lambda function references
- ✅ Global CORS enabled
- ✅ Automatic permission management via SAM
- ✅ Path parameter mapping
- ✅ Specific IAM policies per function
- ✅ Lambda layers for shared code
