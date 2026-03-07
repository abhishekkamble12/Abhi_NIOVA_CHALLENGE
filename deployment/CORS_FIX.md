# CORS Issue - Complete Fix

## Problem
Frontend at `http://hivemind-frontend-83016.s3-website.ap-south-1.amazonaws.com` cannot access API at `https://wcp5c3ga8b.execute-api.ap-south-1.amazonaws.com/prod` due to CORS policy.

## Root Cause
Lambda functions are NOT returning CORS headers in their responses.

## Solution

### Option 1: Quick Fix - Enable CORS in API Gateway (Recommended)

Run this AWS CLI command to enable CORS on the entire API:

```powershell
$API_ID = "wcp5c3ga8b"
$REGION = "ap-south-1"

# Enable CORS on API Gateway
aws apigateway update-rest-api `
    --rest-api-id $API_ID `
    --patch-operations `
        op=add,path=/*/OPTIONS,value=MOCK `
    --region $REGION

# Deploy changes
aws apigateway create-deployment `
    --rest-api-id $API_ID `
    --stage-name prod `
    --description "Enable CORS" `
    --region $REGION
```

### Option 2: Fix Lambda Functions (Proper Solution)

Each Lambda function must return CORS headers:

```python
def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps({'message': 'Success'})
    }
```

### Option 3: Use CloudFront (Production Solution)

Deploy CloudFront in front of both S3 and API Gateway:

```
CloudFront Distribution
├─ Origin 1: S3 (frontend) → /*
└─ Origin 2: API Gateway → /api/*
```

This eliminates CORS issues entirely (same origin).

## Quick Test

After enabling CORS, test with:

```bash
curl -X OPTIONS https://wcp5c3ga8b.execute-api.ap-south-1.amazonaws.com/prod/social/brands \
  -H "Origin: http://hivemind-frontend-83016.s3-website.ap-south-1.amazonaws.com" \
  -H "Access-Control-Request-Method: GET" \
  -v
```

You should see:
```
< Access-Control-Allow-Origin: *
< Access-Control-Allow-Methods: GET,POST,PUT,DELETE,OPTIONS
< Access-Control-Allow-Headers: Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token
```

## Current Status

✅ Frontend deployed and connected to API  
✅ API Gateway created  
✅ Lambda functions deployed  
❌ CORS headers missing  
❌ Lambda functions returning errors (database not configured)

## Next Steps

1. **Enable CORS** (this fix)
2. **Deploy Aurora PostgreSQL** (database)
3. **Update Lambda environment variables** (DB credentials)
4. **Test end-to-end**

## Why This Happened

API Gateway with Lambda proxy integration requires Lambda functions to return CORS headers. The template-api-gateway.yaml has CORS configured in the API definition, but Lambda functions must also return the headers.

## Temporary Workaround

Use browser extension to disable CORS for testing:
- Chrome: "CORS Unblock"
- Firefox: "CORS Everywhere"

**DO NOT use in production!**
