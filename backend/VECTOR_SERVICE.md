# Vector Embedding Service Documentation

## Overview

Production-grade vector embedding service using SentenceTransformers with pgvector for semantic search across articles, posts, and video scenes.

## Architecture

```
app/services/vector_service.py
├── VectorService Class
│   ├── Model: all-MiniLM-L6-v2 (384-dim)
│   ├── generate_embedding()
│   ├── generate_batch_embeddings()
│   ├── search_similar_articles()
│   ├── search_similar_posts()
│   ├── search_similar_video_scenes()
│   └── find_similar_by_embedding()
└── Convenience Functions
```

## Key Features

✅ **SentenceTransformers** - Using all-MiniLM-L6-v2 model  
✅ **384-dimensional embeddings** - Optimal balance of quality vs performance  
✅ **Single embedding generation** - generate_embedding(text)  
✅ **Batch embedding generation** - generate_batch_embeddings(texts)  
✅ **Semantic search with pgvector** - Cosine similarity using <=> operator  
✅ **Article similarity search** - Find similar news articles  
✅ **Post similarity search** - Find similar social media posts  
✅ **Video scene similarity** - Find similar video scenes  
✅ **Efficient batch processing** - Batch size optimization  
✅ **Redis caching** - Cache embeddings for 24 hours  
✅ **Lazy model loading** - Load model only when needed  

## Model Information

**Model**: all-MiniLM-L6-v2
- **Dimension**: 384
- **Max Sequence Length**: 256 tokens
- **Performance**: ~14,000 sentences/sec on CPU
- **Quality**: 68.06 on STS benchmark
- **Size**: ~80MB

## Usage

### Import

```python
from app.services.vector_service import (
    generate_embedding,
    generate_batch_embeddings,
    search_similar_articles,
    search_similar_posts,
    search_similar_video_scenes,
    vector_service
)
```

### Generate Single Embedding

```python
text = "AI is transforming content creation"
embedding = generate_embedding(text)

print(len(embedding))  # 384
print(type(embedding))  # list[float]
```

### Generate Batch Embeddings

```python
texts = [
    "First article about AI",
    "Second article about machine learning",
    "Third article about deep learning"
]

embeddings = generate_batch_embeddings(texts, batch_size=32)

print(len(embeddings))  # 3
print(len(embeddings[0]))  # 384
```

### Search Similar Articles

```python
from app.core.database import get_db

async def search_articles(query: str):
    async with get_db() as db:
        results = await search_similar_articles(
            db=db,
            query_text=query,
            limit=10,
            min_similarity=0.5
        )
        
        for article, similarity in results:
            print(f"{article.title}: {similarity:.4f}")
```

### Search Similar Posts

```python
async def search_posts(query: str, platform: str = None):
    async with get_db() as db:
        results = await search_similar_posts(
            db=db,
            query_text=query,
            platform=platform,  # Optional: "instagram", "linkedin", etc.
            limit=10,
            min_similarity=0.5
        )
        
        for post, similarity in results:
            print(f"{post.content[:50]}: {similarity:.4f}")
```

### Search Similar Video Scenes

```python
async def search_scenes(query: str, video_id: str = None):
    async with get_db() as db:
        results = await search_similar_video_scenes(
            db=db,
            query_text=query,
            video_id=video_id,  # Optional: filter by video
            limit=10,
            min_similarity=0.5
        )
        
        for scene, similarity in results:
            print(f"{scene.description}: {similarity:.4f}")
```

## Semantic Search with pgvector

### Cosine Similarity Query

The service uses pgvector's cosine distance operator (`<=>`):

```sql
SELECT id, 1 - (embedding <=> :query_embedding) AS similarity
FROM articles
WHERE embedding IS NOT NULL
  AND 1 - (embedding <=> :query_embedding) >= :min_similarity
ORDER BY embedding <=> :query_embedding
LIMIT :limit
```

**Operators:**
- `<=>` - Cosine distance (0 = identical, 2 = opposite)
- `1 - (embedding <=> query)` - Cosine similarity (0 to 1)

### Similarity Scores

| Similarity | Interpretation |
|------------|----------------|
| 0.9 - 1.0 | Nearly identical |
| 0.7 - 0.9 | Very similar |
| 0.5 - 0.7 | Moderately similar |
| 0.3 - 0.5 | Somewhat similar |
| 0.0 - 0.3 | Not similar |

## Creating Content with Embeddings

### Create Article

```python
from app.models import Article
from app.services.vector_service import generate_embedding

async def create_article(title: str, content: str, url: str, db):
    # Generate embedding
    text = f"{title} {content}"
    embedding = generate_embedding(text)
    
    # Create article
    article = Article(
        title=title,
        content=content,
        url=url,
        embedding=embedding
    )
    
    db.add(article)
    await db.commit()
    return article
```

### Batch Create Articles

```python
from app.services.vector_service import generate_batch_embeddings

async def create_articles_batch(articles_data: list[dict], db):
    # Prepare texts
    texts = [f"{a['title']} {a['content']}" for a in articles_data]
    
    # Generate embeddings in batch (efficient!)
    embeddings = generate_batch_embeddings(texts, batch_size=32)
    
    # Create articles
    articles = []
    for data, embedding in zip(articles_data, embeddings):
        article = Article(
            title=data['title'],
            content=data['content'],
            url=data['url'],
            embedding=embedding
        )
        articles.append(article)
    
    db.add_all(articles)
    await db.commit()
    return articles
```

## Advanced Usage

### Find Similar by Embedding

```python
from app.models import GeneratedPost

async def find_similar_posts(source_post_id: str, db):
    # Get source post
    source_post = await db.get(GeneratedPost, source_post_id)
    
    # Find similar using embedding
    similar = await vector_service.find_similar_by_embedding(
        db=db,
        embedding=source_post.embedding,
        model_class=GeneratedPost,
        limit=10,
        min_similarity=0.5
    )
    
    return similar
```

### Hybrid Search (Keyword + Semantic)

```python
from sqlalchemy import select, or_

async def hybrid_search(query: str, db):
    # Semantic search
    semantic_results = await search_similar_articles(
        db=db,
        query_text=query,
        limit=20,
        min_similarity=0.3
    )
    
    # Keyword search
    keyword_query = select(Article).filter(
        or_(
            Article.title.ilike(f"%{query}%"),
            Article.content.ilike(f"%{query}%")
        )
    ).limit(20)
    
    keyword_results = await db.execute(keyword_query)
    keyword_articles = keyword_results.scalars().all()
    
    # Combine and deduplicate
    seen_ids = set()
    combined = []
    
    for article, similarity in semantic_results:
        if article.id not in seen_ids:
            combined.append((article, similarity, "semantic"))
            seen_ids.add(article.id)
    
    for article in keyword_articles:
        if article.id not in seen_ids:
            combined.append((article, None, "keyword"))
            seen_ids.add(article.id)
    
    return combined[:10]
```

## Performance Optimization

### Batch Size

```python
# Small batch (< 100 texts)
embeddings = generate_batch_embeddings(texts, batch_size=16)

# Medium batch (100-1000 texts)
embeddings = generate_batch_embeddings(texts, batch_size=32)

# Large batch (> 1000 texts)
embeddings = generate_batch_embeddings(texts, batch_size=64)
```

### Caching

Embeddings are automatically cached in Redis for 24 hours:

```python
# First call: generates embedding
embedding1 = generate_embedding("AI is amazing")

# Second call: returns cached embedding (fast!)
embedding2 = generate_embedding("AI is amazing")
```

### Model Loading

Model is lazy-loaded on first use:

```python
# Model not loaded yet
service = VectorService()

# Model loaded on first embedding generation
embedding = service.generate_embedding("text")
```

## Indexes for Performance

Create vector indexes for fast similarity search:

```sql
-- IVFFlat index (good for < 1M vectors)
CREATE INDEX idx_articles_embedding 
ON articles USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

CREATE INDEX idx_generated_posts_embedding 
ON generated_posts USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

CREATE INDEX idx_video_scenes_embedding 
ON video_scenes USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- HNSW index (better recall, more memory)
CREATE INDEX idx_articles_embedding_hnsw 
ON articles USING hnsw (embedding vector_cosine_ops);
```

## API Endpoints

### Generate Embedding

```http
POST /api/v1/embeddings/generate
Content-Type: application/json

{
  "text": "AI is transforming content creation"
}

Response:
{
  "embedding": [0.1, 0.2, ...],
  "dimension": 384
}
```

### Search Similar Articles

```http
GET /api/v1/articles/search?query=AI&limit=10&min_similarity=0.5

Response:
{
  "query": "AI",
  "count": 10,
  "results": [
    {
      "id": "uuid",
      "title": "Article Title",
      "url": "https://...",
      "similarity": 0.8542
    }
  ]
}
```

### Search Similar Posts

```http
GET /api/v1/posts/search?query=marketing&platform=linkedin&limit=5

Response:
{
  "query": "marketing",
  "platform": "linkedin",
  "count": 5,
  "results": [
    {
      "id": "uuid",
      "content": "Post content...",
      "platform": "linkedin",
      "similarity": 0.7823
    }
  ]
}
```

## Testing

### Test Embedding Generation

```python
def test_generate_embedding():
    text = "Test text"
    embedding = generate_embedding(text)
    
    assert len(embedding) == 384
    assert all(isinstance(x, float) for x in embedding)
```

### Test Batch Generation

```python
def test_batch_embeddings():
    texts = ["Text 1", "Text 2", "Text 3"]
    embeddings = generate_batch_embeddings(texts)
    
    assert len(embeddings) == 3
    assert all(len(emb) == 384 for emb in embeddings)
```

### Test Similarity Search

```python
async def test_search_similar_articles(db):
    results = await search_similar_articles(
        db=db,
        query_text="AI technology",
        limit=5
    )
    
    assert len(results) <= 5
    assert all(0 <= sim <= 1 for _, sim in results)
```

## Troubleshooting

### Model Download

First run downloads the model (~80MB):

```python
# Downloads to ~/.cache/torch/sentence_transformers/
embedding = generate_embedding("test")
```

### Memory Usage

```python
# Model uses ~300MB RAM
# Each embedding: 384 floats * 4 bytes = 1.5KB
# 1000 embeddings = ~1.5MB
```

### Performance

```python
# CPU: ~14,000 sentences/sec
# GPU: ~40,000 sentences/sec (if available)

# Batch processing is much faster:
# Single: 1000 texts = ~70ms each = 70 seconds
# Batch: 1000 texts in one call = ~2 seconds
```

## Summary

The vector embedding service provides:
- ✅ SentenceTransformers with all-MiniLM-L6-v2
- ✅ 384-dimensional embeddings
- ✅ Single and batch embedding generation
- ✅ Semantic search with pgvector
- ✅ Article, post, and video scene similarity
- ✅ Efficient batch processing
- ✅ Redis caching
- ✅ Production-ready performance
