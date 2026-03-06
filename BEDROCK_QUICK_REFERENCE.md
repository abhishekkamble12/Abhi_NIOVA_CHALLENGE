# 🚀 Bedrock Integration Quick Reference

## 1. Bedrock Client Setup

```python
import boto3
import json
from botocore.config import Config

# Configure client
bedrock_config = Config(
    region_name='us-east-1',
    retries={'max_attempts': 3, 'mode': 'adaptive'}
)

bedrock = boto3.client('bedrock-runtime', config=bedrock_config)
```

## 2. Embedding Generation

```python
def generate_embedding(text: str) -> list[float]:
    """Generate 1536-dim embedding using Bedrock Titan"""
    response = bedrock.invoke_model(
        modelId='amazon.titan-embed-text-v1',
        body=json.dumps({'inputText': text})
    )
    result = json.loads(response['body'].read())
    return result['embedding']  # 1536 dimensions

# Usage
embedding = generate_embedding("AI trends in 2024")
print(len(embedding))  # 1536
```

## 3. Content Generation

```python
def generate_text(prompt: str, max_tokens: int = 1024) -> str:
    """Generate text using Claude 3"""
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        body=json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': max_tokens,
            'messages': [{'role': 'user', 'content': prompt}]
        })
    )
    result = json.loads(response['body'].read())
    return result['content'][0]['text']

# Usage
post = generate_text("Write an Instagram post about AI")
```

## 4. Drop-in Replacement

**Replace this:**
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode(text).tolist()  # 384-dim
```

**With this:**
```python
from shared.bedrock_service import generate_embedding
embedding = generate_embedding(text)  # 1536-dim
```

## 5. Service Integration

**Article Service:**
```python
from shared.bedrock_service import generate_embedding

async def create_article(article_data):
    text = f"{article_data.title} {article_data.content}"
    embedding = generate_embedding(text)
    
    article = Article(
        title=article_data.title,
        content=article_data.content,
        embedding=embedding  # 1536-dim
    )
    return article
```

**Brand Service:**
```python
from shared.bedrock_service import generate_embedding

async def create_brand(brand_data):
    text = f"{brand_data.name} {brand_data.description}"
    embedding = generate_embedding(text)
    
    brand = Brand(
        name=brand_data.name,
        embedding=embedding
    )
    return brand
```

## 6. Vector Search (No Changes Needed)

```python
# Works with both 384-dim and 1536-dim embeddings
async def search_similar_articles(db, query_text, limit=10):
    query_embedding = generate_embedding(query_text)
    
    results = await db.execute(text("""
        SELECT *, 1 - (embedding <=> :embedding) AS similarity
        FROM articles
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> :embedding
        LIMIT :limit
    """), {'embedding': query_embedding, 'limit': limit})
    
    return results.fetchall()
```

## 7. Database Migration

```sql
-- Update vector dimension
ALTER TABLE articles ALTER COLUMN embedding TYPE vector(1536);
ALTER TABLE brands ALTER COLUMN embedding TYPE vector(1536);
ALTER TABLE generated_posts ALTER COLUMN embedding TYPE vector(1536);
ALTER TABLE video_scenes ALTER COLUMN embedding TYPE vector(1536);
```

## 8. Environment Variables

```bash
AWS_REGION=us-east-1
BEDROCK_EMBEDDING_MODEL=amazon.titan-embed-text-v1
BEDROCK_TEXT_MODEL=anthropic.claude-3-sonnet-20240229-v1:0
VECTOR_DIMENSION=1536
```

## 9. IAM Permissions

```json
{
  "Effect": "Allow",
  "Action": ["bedrock:InvokeModel"],
  "Resource": [
    "arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v1",
    "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-*"
  ]
}
```

## 10. Cost Comparison

```
SentenceTransformers:
  - Infrastructure: $30/month (EC2)
  - Maintenance: Manual updates
  - Scaling: Manual

Bedrock:
  - Embeddings: $0.0001 per 1K tokens
  - Text: $0.003 per 1K tokens (Claude 3)
  - Maintenance: Automatic
  - Scaling: Automatic
  
Example: 100K embeddings/month = $10
```

## 11. Complete Example

```python
import boto3
import json

# Setup
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

# Generate embedding
def embed(text):
    response = bedrock.invoke_model(
        modelId='amazon.titan-embed-text-v1',
        body=json.dumps({'inputText': text})
    )
    return json.loads(response['body'].read())['embedding']

# Generate content
def generate(prompt):
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        body=json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 1024,
            'messages': [{'role': 'user', 'content': prompt}]
        })
    )
    return json.loads(response['body'].read())['content'][0]['text']

# Usage
article_embedding = embed("AI trends article")
social_post = generate("Write a LinkedIn post about AI")
```

## 12. Migration Checklist

```
✅ Install boto3
✅ Configure AWS credentials
✅ Update IAM permissions
✅ Change vector dimension to 1536
✅ Replace import statements
✅ Test embedding generation
✅ Test vector search
✅ Migrate existing embeddings
✅ Deploy to production
```

---

**Files Created:**
- `lambda/shared/bedrock_service.py` - Full Bedrock service
- `lambda/shared/vector_service_bedrock.py` - Updated vector service
- `lambda/BEDROCK_MIGRATION_GUIDE.md` - Complete migration guide

**Key Change:**
```python
# OLD: 384-dim, self-hosted
from sentence_transformers import SentenceTransformer

# NEW: 1536-dim, managed
from shared.bedrock_service import generate_embedding
```
