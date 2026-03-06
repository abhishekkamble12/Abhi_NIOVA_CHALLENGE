# 🤖 Bedrock Migration Guide for HiveMind

## Executive Summary

This guide provides complete instructions for migrating from SentenceTransformers to Amazon Bedrock for embedding generation and content creation.

---

## 📊 1. Comparison: SentenceTransformers vs Bedrock

| Feature | SentenceTransformers | Amazon Bedrock |
|---------|---------------------|----------------|
| **Model** | all-MiniLM-L6-v2 | Titan Embeddings G1 |
| **Dimensions** | 384 | 1536 |
| **Infrastructure** | Self-hosted (90MB model) | Managed API |
| **Cold Start** | 2-5 seconds (model loading) | <100ms |
| **Scaling** | Manual (container size) | Automatic |
| **Cost** | Compute + storage | Pay-per-use ($0.0001/1K tokens) |
| **Maintenance** | Model updates required | Automatic updates |
| **Latency** | 50-200ms | 100-300ms |

---

## 🔄 2. Migration Steps

### Step 1: Update Database Schema

**Current:** 384-dimensional vectors
**New:** 1536-dimensional vectors

```sql
-- Option 1: Add new column (recommended for gradual migration)
ALTER TABLE articles ADD COLUMN embedding_bedrock vector(1536);
ALTER TABLE brands ADD COLUMN embedding_bedrock vector(1536);
ALTER TABLE generated_posts ADD COLUMN embedding_bedrock vector(1536);
ALTER TABLE video_scenes ADD COLUMN embedding_bedrock vector(1536);

-- Option 2: Alter existing column (requires re-generation)
ALTER TABLE articles ALTER COLUMN embedding TYPE vector(1536);
```

### Step 2: Install Bedrock Dependencies

```bash
pip install boto3==1.34.0
```

### Step 3: Configure AWS Credentials

```bash
# Set environment variables
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret

# Or use IAM role (recommended for Lambda/EC2)
# No credentials needed - uses instance role
```

### Step 4: Replace Vector Service

**Old:** `app/services/vector_service.py`
```python
from sentence_transformers import SentenceTransformer

class VectorService:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384
```

**New:** `app/services/vector_service.py`
```python
from shared.bedrock_service import get_bedrock_service

class VectorService:
    def __init__(self):
        self.bedrock = get_bedrock_service()
        self.dimension = 1536
```

### Step 5: Update Service Layer

**Brand Service:**
```python
# OLD
from app.services.vector_service import generate_embedding

# NEW
from shared.bedrock_service import generate_embedding

# Usage remains the same
embedding = generate_embedding(text)
```

**Article Service:**
```python
# OLD
from app.services.vector_service import search_similar_articles

# NEW
from shared.vector_service_bedrock import search_similar_articles

# Usage remains the same
results = await search_similar_articles(db, query, limit=10)
```

---

## 💻 3. Code Examples

### 3.1 Embedding Generation

```python
from shared.bedrock_service import BedrockService

# Initialize service
bedrock = BedrockService()

# Generate single embedding
text = "AI trends in 2024"
embedding = bedrock.generate_embedding(text)
print(f"Embedding dimension: {len(embedding)}")  # 1536

# Generate batch embeddings
texts = ["Article 1", "Article 2", "Article 3"]
embeddings = bedrock.generate_batch_embeddings(texts)
print(f"Generated {len(embeddings)} embeddings")
```

### 3.2 Content Generation

```python
from shared.bedrock_service import BedrockService, TEXT_MODEL_FAST, TEXT_MODEL_ADVANCED

bedrock = BedrockService()

# Fast generation (Titan Text)
prompt = "Write a social media post about AI"
result = bedrock.generate_text(
    prompt=prompt,
    model=TEXT_MODEL_FAST,
    temperature=0.7,
    max_tokens=500
)
print(result['content'])

# Advanced generation (Claude 3 Sonnet)
system_prompt = "You are a social media expert"
result = bedrock.generate_text(
    prompt=prompt,
    model=TEXT_MODEL_ADVANCED,
    temperature=0.7,
    max_tokens=1024,
    system_prompt=system_prompt
)
print(result['content'])
print(f"Tokens used: {result['usage']}")
```

### 3.3 RAG Pipeline

```python
from shared.bedrock_service import BedrockService
from shared.vector_service_bedrock import search_similar_articles

async def generate_content_with_rag(query: str, db):
    """
    Generate content using RAG pattern
    """
    bedrock = BedrockService()
    
    # Step 1: Retrieve similar articles
    similar_articles = await search_similar_articles(
        db=db,
        query_text=query,
        limit=5,
        min_similarity=0.7
    )
    
    # Step 2: Build context
    context = "\n\n".join([
        f"Article: {article.title}\n{article.summary}"
        for article, similarity in similar_articles
    ])
    
    # Step 3: Generate with context
    prompt = f"""Based on these articles:

{context}

Generate a social media post about: {query}"""
    
    result = bedrock.generate_text(
        prompt=prompt,
        model='anthropic.claude-3-sonnet-20240229-v1:0',
        temperature=0.7,
        max_tokens=500
    )
    
    return result['content']
```

### 3.4 Lambda Function Integration

```python
# Lambda: article_create.py

import sys
sys.path.insert(0, '/opt/python')

from shared.bedrock_service import generate_embedding
from shared.database import get_db_session
from app.models import Article

async def create_article_handler(body: dict):
    """
    Create article with Bedrock embedding
    """
    # Generate embedding using Bedrock
    text_for_embedding = f"{body['title']} {body['content']}"
    embedding = generate_embedding(text_for_embedding)
    
    # Create article
    async with get_db_session() as db:
        article = Article(
            title=body['title'],
            content=body['content'],
            embedding=embedding  # 1536-dimensional
        )
        
        db.add(article)
        await db.flush()
        
        return {'id': str(article.id), 'title': article.title}

def handler(event, context):
    import asyncio
    from shared.response import success_response, parse_body
    
    body = parse_body(event)
    result = asyncio.run(create_article_handler(body))
    return success_response(result, 201)
```

---

## 🔧 4. Configuration

### Environment Variables

```bash
# AWS Configuration
AWS_REGION=us-east-1

# Bedrock Models
BEDROCK_EMBEDDING_MODEL=amazon.titan-embed-text-v1
BEDROCK_TEXT_MODEL=amazon.titan-text-express-v1
BEDROCK_ADVANCED_MODEL=anthropic.claude-3-sonnet-20240229-v1:0

# Vector Dimension
VECTOR_DIMENSION=1536
```

### IAM Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v1",
        "arn:aws:bedrock:*::foundation-model/amazon.titan-text-express-v1",
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
      ]
    }
  ]
}
```

---

## 📊 5. Data Migration

### Migrate Existing Embeddings

```python
import asyncio
from sqlalchemy import select
from shared.bedrock_service import generate_embedding
from shared.database import get_db_session
from app.models import Article

async def migrate_article_embeddings():
    """
    Regenerate embeddings for existing articles
    """
    async with get_db_session() as db:
        # Get all articles
        result = await db.execute(select(Article))
        articles = result.scalars().all()
        
        print(f"Migrating {len(articles)} articles...")
        
        for i, article in enumerate(articles):
            # Generate new embedding
            text = f"{article.title} {article.content}"
            new_embedding = generate_embedding(text)
            
            # Update article
            article.embedding = new_embedding
            
            if (i + 1) % 100 == 0:
                await db.flush()
                print(f"Processed {i + 1} articles")
        
        await db.commit()
        print("Migration complete!")

# Run migration
asyncio.run(migrate_article_embeddings())
```

### Batch Migration Script

```python
# scripts/migrate_to_bedrock.py

import asyncio
from sqlalchemy import select, func
from shared.bedrock_service import generate_batch_embeddings
from shared.database import get_db_session
from app.models import Article, Brand, GeneratedPost

async def migrate_all_embeddings():
    """
    Migrate all embeddings to Bedrock
    """
    async with get_db_session() as db:
        # Migrate articles
        print("Migrating articles...")
        articles = await db.execute(select(Article))
        article_list = articles.scalars().all()
        
        texts = [f"{a.title} {a.content}" for a in article_list]
        embeddings = generate_batch_embeddings(texts)
        
        for article, embedding in zip(article_list, embeddings):
            article.embedding = embedding
        
        await db.flush()
        print(f"Migrated {len(article_list)} articles")
        
        # Migrate brands
        print("Migrating brands...")
        brands = await db.execute(select(Brand))
        brand_list = brands.scalars().all()
        
        texts = [f"{b.name} {b.description or ''}" for b in brand_list]
        embeddings = generate_batch_embeddings(texts)
        
        for brand, embedding in zip(brand_list, embeddings):
            brand.embedding = embedding
        
        await db.flush()
        print(f"Migrated {len(brand_list)} brands")
        
        await db.commit()
        print("All migrations complete!")

if __name__ == '__main__':
    asyncio.run(migrate_all_embeddings())
```

---

## 💰 6. Cost Analysis

### SentenceTransformers Cost

```
Lambda with model:
  - Memory: 1024MB (for model)
  - Duration: 500ms average
  - Cost per 1M requests: $8.33

EC2 hosting:
  - t3.medium: $30/month
  - Always running
```

### Bedrock Cost

```
Embeddings:
  - $0.0001 per 1,000 tokens
  - Average: 100 tokens per text
  - Cost per 1M embeddings: $10

Text Generation (Titan):
  - Input: $0.0008 per 1K tokens
  - Output: $0.0016 per 1K tokens
  - Average: 500 tokens total
  - Cost per 1M generations: $800

Text Generation (Claude 3 Haiku):
  - Input: $0.00025 per 1K tokens
  - Output: $0.00125 per 1K tokens
  - Cost per 1M generations: $625
```

### Cost Comparison

```
Scenario: 100K embeddings + 10K text generations per month

SentenceTransformers:
  - Lambda: $0.83
  - Total: $0.83

Bedrock:
  - Embeddings: $1.00
  - Text (Titan): $8.00
  - Total: $9.00

Trade-off: Pay 10x more for:
  - No infrastructure management
  - Better quality (1536-dim vs 384-dim)
  - Automatic scaling
  - Latest models
```

---

## ✅ 7. Testing

### Unit Tests

```python
# tests/test_bedrock_service.py

import pytest
from shared.bedrock_service import BedrockService

def test_generate_embedding():
    bedrock = BedrockService()
    
    text = "Test article about AI"
    embedding = bedrock.generate_embedding(text)
    
    assert len(embedding) == 1536
    assert all(isinstance(x, float) for x in embedding)

def test_generate_text():
    bedrock = BedrockService()
    
    prompt = "Write a short sentence about AI"
    result = bedrock.generate_text(prompt, max_tokens=50)
    
    assert 'content' in result
    assert len(result['content']) > 0
    assert 'usage' in result

@pytest.mark.asyncio
async def test_vector_search():
    from shared.vector_service_bedrock import search_similar_articles
    from shared.database import get_db_session
    
    async with get_db_session() as db:
        results = await search_similar_articles(
            db=db,
            query_text="AI trends",
            limit=5
        )
        
        assert isinstance(results, list)
        for article, similarity in results:
            assert 0.0 <= similarity <= 1.0
```

---

## 🚀 8. Deployment Checklist

```yaml
✅ Install boto3 dependency
✅ Configure AWS credentials
✅ Update IAM permissions for Bedrock
✅ Update database schema (1536 dimensions)
✅ Replace vector_service.py with bedrock version
✅ Update all service imports
✅ Migrate existing embeddings
✅ Test embedding generation
✅ Test vector search
✅ Test content generation
✅ Update Lambda layers
✅ Deploy to production
✅ Monitor costs
✅ Monitor performance
```

---

*Document Version: 1.0*  
*Migration: SentenceTransformers → Amazon Bedrock*  
*Embedding Model: Titan Embeddings G1 (1536-dim)*
