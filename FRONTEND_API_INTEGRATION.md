# Frontend API Integration Guide

## Problem Statement

The frontend was hardcoded to use FastAPI localhost endpoint:
```typescript
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

This prevents deployment to production with API Gateway.

## Solution

### Updated API Client (`app/lib/api.ts`)

**Before**:
```typescript
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

**After**:
```typescript
const getApiBaseUrl = () => {
  if (typeof window === 'undefined') {
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();
```

### Key Changes

1. **Dynamic API URL**: Uses `NEXT_PUBLIC_API_URL` environment variable
2. **Removed `/api/v1` suffix**: API Gateway routes don't use this prefix
3. **Server/Client compatibility**: Works in both SSR and CSR
4. **Debug logging**: Logs API endpoint in browser console

## Environment Configuration

### Local Development

**File**: `.env.local`
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

This points to your local FastAPI backend.

### Production

**File**: `.env.production`
```bash
NEXT_PUBLIC_API_URL=https://{api-id}.execute-api.ap-south-1.amazonaws.com/prod
```

Replace `{api-id}` with your actual API Gateway ID.

### Get API Gateway ID

After deploying the CloudFormation stack:

```bash
aws cloudformation describe-stacks \
  --stack-name hivemind-api \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text
```

Output:
```
https://abc123xyz.execute-api.ap-south-1.amazonaws.com/prod
```

## API Routes Mapping

### FastAPI (Old) → API Gateway (New)

| FastAPI Route | API Gateway Route | Lambda Function |
|---------------|-------------------|-----------------|
| `POST /api/v1/social/brands` | `POST /social/brands` | `social_create_brand` |
| `GET /api/v1/social/brands/{id}` | `GET /social/brands/{id}` | `social_get_brand` |
| `POST /api/v1/social/generate/content` | `POST /social/generate/content` | `social_generate_content` |
| `GET /api/v1/feed/real/personalized/{userId}` | `GET /feed/real/personalized/{userId}` | `feed_personalized` |
| `POST /api/v1/videos/videos/upload` | `POST /videos/videos/upload` | `video_upload` |

**Note**: `/api/v1` prefix is removed in API Gateway routes.

## Usage Examples

### Create Brand
```typescript
import { apiClient } from '@/app/lib/api';

const brand = await apiClient.brand.create({
  name: 'TechCorp',
  industry: 'technology',
  tone: 'professional',
  target_audience: 'developers'
});
```

**Request**:
- Local: `POST http://localhost:8000/social/brands`
- Production: `POST https://{api-id}.execute-api.ap-south-1.amazonaws.com/prod/social/brands`

### Get Personalized Feed
```typescript
const feed = await apiClient.feed.getPersonalizedFeed(userId, 20);
```

**Request**:
- Local: `GET http://localhost:8000/feed/real/personalized/123?limit=20`
- Production: `GET https://{api-id}.execute-api.ap-south-1.amazonaws.com/prod/feed/real/personalized/123?limit=20`

### Upload Video
```typescript
const formData = new FormData();
formData.append('file', videoFile);

const result = await apiClient.videos.upload(formData);
```

**Request**:
- Local: `POST http://localhost:8000/videos/videos/upload`
- Production: `POST https://{api-id}.execute-api.ap-south-1.amazonaws.com/prod/videos/videos/upload`

## Deployment

### Step 1: Deploy Backend (API Gateway + Lambda)

```bash
cd backend-aws

# Build
sam build -t template-api-gateway.yaml

# Deploy
sam deploy --guided --template-file template-api-gateway.yaml --stack-name hivemind-api

# Get API URL
aws cloudformation describe-stacks \
  --stack-name hivemind-api \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text
```

### Step 2: Configure Frontend

Create `.env.production`:
```bash
NEXT_PUBLIC_API_URL=https://abc123xyz.execute-api.ap-south-1.amazonaws.com/prod
```

### Step 3: Build Frontend

```bash
# Build for production
npm run build

# Test production build locally
npm run start
```

### Step 4: Deploy to AWS Amplify

```bash
# Install Amplify CLI
npm install -g @aws-amplify/cli

# Initialize Amplify
amplify init

# Add hosting
amplify add hosting

# Publish
amplify publish
```

Or deploy to Vercel/Netlify with environment variable:
```bash
# Vercel
vercel --prod -e NEXT_PUBLIC_API_URL=https://abc123xyz.execute-api.ap-south-1.amazonaws.com/prod

# Netlify
netlify deploy --prod --env NEXT_PUBLIC_API_URL=https://abc123xyz.execute-api.ap-south-1.amazonaws.com/prod
```

## Testing

### Local Testing (FastAPI)

```bash
# Terminal 1: Start FastAPI backend
cd backend
python run.py

# Terminal 2: Start Next.js frontend
npm run dev
```

Visit: `http://localhost:3000`

API calls go to: `http://localhost:8000`

### Production Testing (API Gateway)

```bash
# Set production API URL
export NEXT_PUBLIC_API_URL=https://abc123xyz.execute-api.ap-south-1.amazonaws.com/prod

# Start Next.js
npm run dev
```

Visit: `http://localhost:3000`

API calls go to: `https://abc123xyz.execute-api.ap-south-1.amazonaws.com/prod`

### Verify API Endpoint

Open browser console and check:
```
🔗 API Endpoint: https://abc123xyz.execute-api.ap-south-1.amazonaws.com/prod
```

## Error Handling

### CORS Errors

If you see CORS errors in browser console:

```
Access to fetch at 'https://...' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solution**: Ensure Lambda functions return CORS headers:

```python
return {
    'statusCode': 200,
    'headers': {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    },
    'body': json.dumps(data)
}
```

### 404 Not Found

If API calls return 404:

1. Check API Gateway routes are deployed
2. Verify Lambda functions are attached to routes
3. Check CloudFormation stack outputs

```bash
aws cloudformation describe-stacks --stack-name hivemind-api
```

### Network Errors

If API calls fail with network errors:

1. Check API Gateway endpoint is accessible:
```bash
curl https://abc123xyz.execute-api.ap-south-1.amazonaws.com/prod/social/brands
```

2. Check Lambda function logs:
```bash
sam logs -n SocialCreateBrandFunction --stack-name hivemind-api --tail
```

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | API Gateway endpoint | `https://{api-id}.execute-api.ap-south-1.amazonaws.com/prod` |

**Important**: 
- Must start with `NEXT_PUBLIC_` to be accessible in browser
- No trailing slash
- No `/api/v1` suffix

## Migration Checklist

- [x] Update `app/lib/api.ts` to use `NEXT_PUBLIC_API_URL`
- [x] Remove `/api/v1` suffix from API_BASE_URL
- [x] Create `.env.local.example` for local development
- [x] Create `.env.production.example` for production
- [x] Add debug logging for API endpoint
- [ ] Deploy API Gateway stack
- [ ] Get API Gateway URL from CloudFormation outputs
- [ ] Create `.env.production` with actual API Gateway URL
- [ ] Test API calls in development
- [ ] Test API calls in production
- [ ] Deploy frontend to AWS Amplify/Vercel/Netlify

## Troubleshooting

### Issue: API calls still go to localhost in production

**Cause**: `.env.production` not created or not loaded

**Solution**:
1. Create `.env.production` with correct API Gateway URL
2. Rebuild: `npm run build`
3. Restart: `npm run start`

### Issue: Environment variable not updating

**Cause**: Next.js caches environment variables

**Solution**:
```bash
# Clear Next.js cache
rm -rf .next

# Rebuild
npm run build
```

### Issue: CORS errors in production

**Cause**: Lambda functions missing CORS headers

**Solution**: Ensure all Lambda responses include:
```python
'Access-Control-Allow-Origin': '*'
```

## Summary

### Before
- ❌ Hardcoded `http://localhost:8000/api/v1`
- ❌ Cannot deploy to production
- ❌ No environment configuration

### After
- ✅ Dynamic API URL via `NEXT_PUBLIC_API_URL`
- ✅ Works with both FastAPI (local) and API Gateway (production)
- ✅ Environment-specific configuration
- ✅ Debug logging
- ✅ Production-ready

The frontend now seamlessly switches between local FastAPI backend and production API Gateway based on environment configuration.
