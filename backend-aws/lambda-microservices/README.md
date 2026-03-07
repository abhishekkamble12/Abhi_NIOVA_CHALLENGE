# 🚀 Lambda Microservices Architecture

## Project Structure

```
lambda-microservices/
├── handlers/                    # Lambda function handlers
│   ├── social_create_brand.py
│   ├── social_get_brand.py
│   ├── social_list_brands.py
│   ├── social_generate_content.py
│   └── social_get_post.py
├── services/                    # Business logic
│   └── social_service.py
├── shared/                      # Shared utilities
│   └── lambda_utils.py
├── layer/                       # Lambda layer (dependencies)
│   └── python/
├── template.yaml               # SAM template
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

---

## Architecture

```
API Gateway
    ↓
Lambda Functions (Microservices)
    ↓
Business Logic (Services)
    ↓
AWS Resources
    ├─→ Aurora PostgreSQL
    ├─→ ElastiCache Redis
    ├─→ S3
    ├─→ Bedrock
    └─→ EventBridge
```

---

## Lambda Functions

### Social Media
| Function | Method | Path | Handler |
|----------|--------|------|---------|
| CreateBrand | POST | `/api/v1/social/brands` | `social_create_brand.handler` |
| GetBrand | GET | `/api/v1/social/brands/{brand_id}` | `social_get_brand.handler` |
| ListBrands | GET | `/api/v1/social/brands` | `social_list_brands.handler` |
| GenerateContent | POST | `/api/v1/social/generate/content` | `social_generate_content.handler` |
| GetPost | GET | `/api/v1/social/posts/{post_id}` | `social_get_post.handler` |

---

## Deployment

### 1. Build Lambda Layer

```bash
# Create layer directory
mkdir -p layer/python

# Install dependencies
pip install -r requirements.txt -t layer/python/

# Copy services and shared code
cp -r services layer/python/
cp -r shared layer/python/
cp -r ../services layer/python/  # AWS services
```

### 2. Deploy with SAM

```bash
# Build
sam build

# Deploy
sam deploy --guided

# Or deploy with parameters
sam deploy \
  --stack-name hivemind-lambda \
  --parameter-overrides \
    DBUsername=postgres \
    DBPassword=your_password \
    VpcId=vpc-xxxxx \
    SubnetIds=subnet-xxxxx,subnet-yyyyy \
  --capabilities CAPABILITY_IAM
```

### 3. Test Functions

```bash
# Invoke locally
sam local invoke CreateBrandFunction -e events/create_brand.json

# Test API locally
sam local start-api

# Test deployed function
aws lambda invoke \
  --function-name hivemind-CreateBrandFunction \
  --payload file://events/create_brand.json \
  response.json
```

---

## Event Examples

### Create Brand
```json
{
  "httpMethod": "POST",
  "path": "/api/v1/social/brands",
  "body": "{\"name\":\"TechCorp\",\"industry\":\"Technology\",\"tone\":\"Professional\",\"target_audience\":\"Developers\"}"
}
```

### Get Brand
```json
{
  "httpMethod": "GET",
  "path": "/api/v1/social/brands/1",
  "pathParameters": {
    "brand_id": "1"
  }
}
```

### Generate Content
```json
{
  "httpMethod": "POST",
  "path": "/api/v1/social/generate/content",
  "queryStringParameters": {
    "brand_id": "1",
    "platform": "linkedin"
  }
}
```

---

## Environment Variables

Set in `template.yaml` or Lambda console:

```bash
AWS_REGION=ap-south-1
DB_HOST=aurora-endpoint
DB_PORT=5432
DB_NAME=hiveminddb
DB_USER=postgres
DB_PASSWORD=password
REDIS_HOST=redis-endpoint
REDIS_PORT=6379
S3_BUCKET=hivemind-media
BEDROCK_MODEL_EMBEDDING=amazon.titan-embed-text-v2:0
BEDROCK_MODEL_TEXT=anthropic.claude-3-sonnet-20240229-v1:0
```

---

## Lambda Response Format

All functions return API Gateway proxy responses:

```python
{
    "statusCode": 200,
    "headers": {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
    },
    "body": "{\"id\": 1, \"name\": \"TechCorp\"}"
}
```

---

## Business Logic Separation

### Handler (Lambda)
- Parse API Gateway event
- Extract parameters
- Call business logic
- Return API Gateway response

### Service (Business Logic)
- Database operations
- External API calls
- Business rules
- Return data

### Example

```python
# Handler
def handler(event, context):
    brand_id = get_path_param(event, 'brand_id')
    result = asyncio.run(get_brand_logic(brand_id))
    return success_response(result)

# Service
async def get_brand_logic(brand_id: int):
    async with get_db_connection() as conn:
        brand = await conn.fetchrow("SELECT * FROM brands WHERE id = $1", brand_id)
    return dict(brand)
```

---

## Cost Optimization

### Lambda Pricing
- **Requests**: $0.20 per 1M requests
- **Duration**: $0.0000166667 per GB-second
- **Free Tier**: 1M requests + 400,000 GB-seconds/month

### Example Cost (1M requests/month)
- Requests: $0.20
- Duration (512MB, 1s avg): $8.33
- **Total**: ~$8.53/month

### vs EC2 (t3.small)
- EC2: ~$15/month (24/7)
- Lambda: ~$8.53/month (pay per use)
- **Savings**: 43%

---

## Monitoring

### CloudWatch Logs
```bash
# View logs
aws logs tail /aws/lambda/hivemind-CreateBrandFunction --follow

# Filter errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/hivemind-CreateBrandFunction \
  --filter-pattern "ERROR"
```

### CloudWatch Metrics
- Invocations
- Duration
- Errors
- Throttles
- Concurrent executions

### X-Ray Tracing
Enable in `template.yaml`:
```yaml
Globals:
  Function:
    Tracing: Active
```

---

## Testing

### Unit Tests
```python
# test_social_service.py
import pytest
from services.social_service import create_brand_logic

@pytest.mark.asyncio
async def test_create_brand():
    result = await create_brand_logic("Test", "Tech", "Pro", "Devs")
    assert result['name'] == "Test"
```

### Integration Tests
```bash
# Test API Gateway integration
curl -X POST https://api-id.execute-api.region.amazonaws.com/prod/api/v1/social/brands \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","industry":"Tech","tone":"Pro","target_audience":"Devs"}'
```

---

## Scaling

### Auto-Scaling
- Lambda scales automatically
- No configuration needed
- Handles 1 to 1000+ concurrent requests

### Concurrency Limits
- Default: 1000 concurrent executions
- Reserved concurrency: Guarantee capacity
- Provisioned concurrency: Pre-warm functions

### Cold Start Optimization
- Use provisioned concurrency
- Minimize dependencies
- Keep functions small
- Use Lambda layers

---

## Security

### IAM Roles
- Least privilege principle
- Separate role per function
- No hardcoded credentials

### VPC Configuration
- Lambda in private subnets
- Access to Aurora/Redis via VPC
- NAT Gateway for internet access

### Secrets Management
- Use AWS Secrets Manager
- Environment variables for non-sensitive config
- Rotate credentials regularly

---

## Migration from FastAPI

### Before (FastAPI)
```python
@app.post("/api/v1/social/brands")
async def create_brand(brand: BrandCreate):
    # Business logic
    return {"id": brand_id}
```

### After (Lambda)
```python
def handler(event, context):
    body = parse_body(event)
    result = asyncio.run(create_brand_logic(**body))
    return success_response(result)
```

### Key Changes
1. ✅ Handler function instead of route decorator
2. ✅ Parse API Gateway event
3. ✅ Return API Gateway response
4. ✅ Business logic in separate service
5. ✅ Use asyncio.run() for async code

---

## Summary

✅ **Microservices**: Each endpoint is a separate Lambda  
✅ **API Gateway**: HTTP API with Lambda proxy integration  
✅ **Business Logic**: Separated into service modules  
✅ **Shared Code**: Lambda layer for dependencies  
✅ **Infrastructure**: SAM template for deployment  
✅ **Cost Effective**: Pay per use, auto-scaling  
✅ **Production Ready**: Monitoring, logging, tracing  

**Deploy**: `sam deploy --guided`
