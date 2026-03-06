# 🚀 FastAPI to AWS Lambda Conversion Guide

## Executive Summary

This document provides a complete guide for converting HiveMind FastAPI endpoints to AWS Lambda functions with API Gateway integration.

---

## 📊 1. Conversion Overview

### FastAPI vs Lambda Comparison

| Aspect | FastAPI | AWS Lambda |
|--------|---------|------------|
| **Request Handling** | `@app.post("/path")` | `def handler(event, context)` |
| **Request Body** | `body: ModelSchema` | `parse_body(event)` |
| **Path Parameters** | `{param}: str` | `get_path_parameter(event, 'param')` |
| **Query Parameters** | `param: str = Query()` | `get_query_parameter(event, 'param')` |
| **Response** | `return {"data": ...}` | `return success_response({"data": ...})` |
| **Database** | `db: Session = Depends(get_db)` | `async with get_db_session() as db:` |
| **Async** | Native async/await | `asyncio.run(async_function())` |

---

## 🔄 2. Endpoint Conversion Examples

### Example 1: POST Endpoint

**FastAPI:**
```python
@app.post("/api/v1/articles", status_code=201)
async def create_article(
    article_data: ArticleCreate,
    db: AsyncSession = Depends(get_db)
):
    embedding = generate_embedding(article_data.title)
    article = Article(**article_data.dict(), embedding=embedding)
    db.add(article)
    await db.commit()
    return article
```

**Lambda:**
```python
def handler(event, context):
    try:
        body = parse_body(event)
        result = asyncio.run(create_article_handler(body))
        return success_response(result, status_code=201)
    except Exception as e:
        return error_response(str(e), status_code=500)

async def create_article_handler(body):
    async with get_db_session() as db:
        embedding = generate_embedding(body['title'])
        article = Article(**body, embedding=embedding)
        db.add(article)
        await db.flush()
        return {'id': str(article.id), ...}
```

### Example 2: GET with Path Parameter

**FastAPI:**
```python
@app.get("/api/v1/articles/{article_id}")
async def get_article(
    article_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    article = await db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404)
    return article
```

**Lambda:**
```python
def handler(event, context):
    try:
        article_id = get_path_parameter(event, 'article_id')
        result = asyncio.run(get_article_handler(article_id))
        return success_response(result)
    except ValueError:
        return error_response('Not found', status_code=404)

async def get_article_handler(article_id):
    async with get_db_session() as db:
        result = await db.execute(
            select(Article).filter(Article.id == article_id)
        )
        article = result.scalar_one_or_none()
        if not article:
            raise ValueError('Article not found')
        return {'id': str(article.id), ...}
```

### Example 3: GET with Query Parameters

**FastAPI:**
```python
@app.get("/api/v1/articles")
async def list_articles(
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    query = select(Article)
    if category:
        query = query.filter(Article.category == category)
    articles = await db.execute(query.offset((page-1)*page_size).limit(page_size))
    return {'articles': articles.scalars().all()}
```

**Lambda:**
```python
def handler(event, context):
    try:
        category = get_query_parameter(event, 'category')
        page = int(get_query_parameter(event, 'page', 1))
        page_size = int(get_query_parameter(event, 'page_size', 20))
        
        result = asyncio.run(list_articles_handler(category, page, page_size))
        return success_response(result)
    except Exception as e:
        return error_response(str(e), status_code=500)

async def list_articles_handler(category, page, page_size):
    async with get_db_session() as db:
        query = select(Article)
        if category:
            query = query.filter(Article.category == category)
        result = await db.execute(
            query.offset((page-1)*page_size).limit(page_size)
        )
        return {'articles': [serialize(a) for a in result.scalars().all()]}
```

---

## 📁 3. Lambda Project Structure

```
lambda/
├── functions/                      # Lambda handlers
│   ├── article_create.py          # POST /articles
│   ├── article_get.py             # GET /articles/{id}
│   ├── article_list.py            # GET /articles
│   ├── article_search.py          # GET /articles/search/semantic
│   ├── article_update.py          # PUT /articles/{id}
│   ├── article_delete.py          # DELETE /articles/{id}
│   ├── brand_create.py            # POST /brands
│   ├── brand_get.py               # GET /brands/{id}
│   ├── brand_list.py              # GET /brands
│   ├── brand_update.py            # PUT /brands/{id}
│   └── brand_delete.py            # DELETE /brands/{id}
│
├── shared/                         # Shared utilities (Lambda layer)
│   ├── __init__.py
│   ├── response.py                # Response formatting
│   ├── database.py                # Database connections
│   ├── auth.py                    # Authentication helpers
│   └── validation.py              # Request validation
│
├── layers/                         # Lambda layers
│   ├── dependencies/              # Python packages
│   │   ├── python/
│   │   └── requirements.txt
│   └── app-code/                  # Application code
│       └── python/
│           ├── app/               # Backend app code
│           └── shared/            # Shared utilities
│
├── events/                         # Test events
│   ├── article-create.json
│   ├── article-get.json
│   └── article-search.json
│
├── tests/                          # Lambda tests
│   ├── test_article_create.py
│   └── test_article_search.py
│
├── template.yaml                   # SAM template
├── samconfig.toml                  # SAM configuration
└── DEPLOYMENT_GUIDE.md            # Deployment instructions
```

---

## 🔌 4. API Gateway Event Structure

### POST Request Event

```json
{
  "resource": "/articles",
  "path": "/articles",
  "httpMethod": "POST",
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGc..."
  },
  "body": "{\"title\":\"AI Trends\",\"content\":\"...\"}",
  "isBase64Encoded": false,
  "requestContext": {
    "authorizer": {
      "claims": {
        "sub": "user-123",
        "email": "user@example.com"
      }
    }
  }
}
```

### GET Request Event

```json
{
  "resource": "/articles/{article_id}",
  "path": "/articles/abc-123",
  "httpMethod": "GET",
  "pathParameters": {
    "article_id": "abc-123"
  },
  "queryStringParameters": {
    "include": "tags"
  },
  "headers": {
    "Accept": "application/json"
  }
}
```

### Lambda Response Format

```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*"
  },
  "body": "{\"id\":\"abc-123\",\"title\":\"...\"}"
}
```

---

## 🛠️ 5. Shared Utilities

### Response Helpers

```python
# shared/response.py

def success_response(body, status_code=200):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body, default=str)
    }

def error_response(message, status_code=400):
    return success_response(
        {'error': message, 'statusCode': status_code},
        status_code
    )
```

### Database Helpers

```python
# shared/database.py

@asynccontextmanager
async def get_db_session():
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        await session.commit()
    except:
        await session.rollback()
        raise
    finally:
        await session.close()
```

### Request Parsing

```python
# shared/response.py

def parse_body(event):
    body = event.get('body', '{}')
    return json.loads(body) if isinstance(body, str) else body

def get_path_parameter(event, param):
    return (event.get('pathParameters') or {}).get(param)

def get_query_parameter(event, param, default=None):
    return (event.get('queryStringParameters') or {}).get(param, default)
```

---

## 🚀 6. Deployment Steps

### Step 1: Prepare Lambda Layers

```bash
# Create dependencies layer
cd lambda/layers/dependencies
pip install -r requirements.txt -t python/
zip -r dependencies-layer.zip python/

# Upload to AWS
aws lambda publish-layer-version \
  --layer-name hivemind-dependencies \
  --zip-file fileb://dependencies-layer.zip \
  --compatible-runtimes python3.11
```

### Step 2: Prepare Application Layer

```bash
# Create app code layer
cd lambda/layers/app-code
cp -r ../../../backend/app python/
cp -r ../../shared python/
zip -r app-code-layer.zip python/

# Upload to AWS
aws lambda publish-layer-version \
  --layer-name hivemind-app-code \
  --zip-file fileb://app-code-layer.zip \
  --compatible-runtimes python3.11
```

### Step 3: Deploy Lambda Functions

```bash
# Using SAM
sam build
sam deploy --guided

# Or using AWS CLI
cd lambda/functions
zip article_create.zip article_create.py

aws lambda create-function \
  --function-name hivemind-article-create \
  --runtime python3.11 \
  --handler article_create.handler \
  --role arn:aws:iam::account:role/lambda-role \
  --zip-file fileb://article_create.zip \
  --layers \
    arn:aws:lambda:region:account:layer:hivemind-dependencies:1 \
    arn:aws:lambda:region:account:layer:hivemind-app-code:1
```

### Step 4: Configure API Gateway

```bash
# Create REST API
aws apigateway create-rest-api \
  --name "HiveMind API" \
  --endpoint-configuration types=REGIONAL

# Create resources and methods
aws apigateway create-resource \
  --rest-api-id abc123 \
  --parent-id root-id \
  --path-part articles

aws apigateway put-method \
  --rest-api-id abc123 \
  --resource-id resource-id \
  --http-method POST \
  --authorization-type COGNITO_USER_POOLS

# Integrate with Lambda
aws apigateway put-integration \
  --rest-api-id abc123 \
  --resource-id resource-id \
  --http-method POST \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri arn:aws:apigateway:region:lambda:path/2015-03-31/functions/arn:aws:lambda:region:account:function:hivemind-article-create/invocations
```

---

## 📊 7. Performance Optimization

### Cold Start Optimization

```python
# Load heavy dependencies outside handler
import sys
sys.path.insert(0, '/opt/python')

from app.services.vector_service import vector_service

# Pre-load model (runs once per container)
vector_service.model  # Triggers lazy loading

def handler(event, context):
    # Handler code here
    pass
```

### Connection Pooling

```python
# Reuse database connections across invocations
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(...)
    return _engine
```

### Response Caching

```python
# Cache responses in ElastiCache
import boto3
import json

elasticache = boto3.client('elasticache')

def handler(event, context):
    cache_key = f"article:{article_id}"
    
    # Check cache
    cached = redis.get(cache_key)
    if cached:
        return success_response(json.loads(cached))
    
    # Fetch from database
    result = fetch_article(article_id)
    
    # Cache result
    redis.setex(cache_key, 300, json.dumps(result))
    
    return success_response(result)
```

---

## ✅ 8. Testing

### Local Testing

```bash
# Test with SAM
sam local invoke ArticleCreateFunction \
  --event events/article-create.json

# Test API locally
sam local start-api
curl -X POST http://localhost:3000/articles \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","content":"..."}'
```

### Unit Testing

```python
# tests/test_article_create.py

import json
from functions.article_create import handler

def test_create_article():
    event = {
        'body': json.dumps({
            'title': 'Test Article',
            'content': 'Test content'
        })
    }
    
    response = handler(event, {})
    
    assert response['statusCode'] == 201
    body = json.loads(response['body'])
    assert 'id' in body
```

---

## 💰 9. Cost Comparison

### FastAPI on EC2

```
EC2 t3.medium: $30/month
RDS: $50/month
Total: $80/month (always running)
```

### Lambda + API Gateway

```
1M requests/month:
  - Lambda: $8.73
  - API Gateway: $3.50
  - RDS Proxy: $21.90
Total: $34.13/month (pay-per-use)

Savings: 57% reduction
```

---

## 🎯 10. Migration Checklist

```yaml
✅ Create Lambda folder structure
✅ Convert endpoints to Lambda handlers
✅ Create shared utilities (response, database)
✅ Build Lambda layers (dependencies + app code)
✅ Deploy Lambda functions
✅ Configure API Gateway
✅ Set up Cognito authorizer
✅ Configure VPC and security groups
✅ Set up RDS Proxy
✅ Configure CloudWatch logging
✅ Set up X-Ray tracing
✅ Test all endpoints
✅ Update frontend API URLs
✅ Monitor performance
✅ Optimize cold starts
```

---

*Document Version: 1.0*  
*Conversion: FastAPI → AWS Lambda*  
*API Gateway: REST API with Lambda Proxy Integration*
