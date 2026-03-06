# Vector Service Quick Reference

## Import

```python
from app.services.vector_service import (
    generate_embedding,
    generate_batch_embeddings,
    search_similar_articles,
    search_similar_posts,
    search_similar_video_scenes
)
```

## Generate Embeddings

### Single Text
```python
embedding = generate_embedding("AI is transforming content")
# Returns: list[float] with 384 dimensions
```

### Batch (Efficient)
```python
texts = ["Text 1", "Text 2", "Text 3"]
embeddings = generate_batch_embeddings(texts, batch_size=32)
# Returns: list[list[float]]
```

## Semantic Search

### Search Articles
```python
results = await search_similar_articles(
    db=db,
    query_text="AI technology",
    limit=10,
    min_similarity=0.5
)
# Returns: list[(Article, float)]
```

### Search Posts
```python
results = await search_similar_posts(
    db=db,
    query_text="marketing tips",
    platform="linkedin",  # Optional
    limit=10,
    min_similarity=0.5
)
# Returns: list[(GeneratedPost, float)]
```

### Search Video Scenes
```python
results = await search_similar_video_scenes(
    db=db,
    query_text="action scene",
    video_id="uuid",  # Optional
    limit=10,
    min_similarity=0.5
)
# Returns: list[(VideoScene, float)]
```

## Create with Embeddings

### Single Article
```python
from app.models import Article

text = f"{title} {content}"
embedding = generate_embedding(text)

article = Article(
    title=title,
    content=content,
    url=url,
    embedding=embedding
)
db.add(article)
await db.commit()
```

### Batch Articles
```python
texts = [f"{a['title']} {a['content']}" for a in articles_data]
embeddings = generate_batch_embeddings(texts, batch_size=32)

articles = [
    Article(title=data['title'], content=data['content'], embedding=emb)
    for data, emb in zip(articles_data, embeddings)
]
db.add_all(articles)
await db.commit()
```

## pgvector Query

```sql
SELECT id, 1 - (embedding <=> :query) AS similarity
FROM articles
WHERE embedding IS NOT NULL
  AND 1 - (embedding <=> :query) >= 0.5
ORDER BY embedding <=> :query
LIMIT 10
```

## Model Info

- **Model**: all-MiniLM-L6-v2
- **Dimension**: 384
- **Performance**: ~14,000 sentences/sec (CPU)
- **Size**: ~80MB

## Similarity Scores

| Score | Meaning |
|-------|---------|
| 0.9-1.0 | Nearly identical |
| 0.7-0.9 | Very similar |
| 0.5-0.7 | Moderately similar |
| 0.3-0.5 | Somewhat similar |
| 0.0-0.3 | Not similar |

## Features

- ✅ Single & batch embedding generation
- ✅ Semantic search with pgvector
- ✅ Redis caching (24 hours)
- ✅ Lazy model loading
- ✅ Efficient batch processing

## Files

- `app/services/vector_service.py` - Vector service implementation
- `app/examples/vector_service_examples.py` - Usage examples
- `VECTOR_SERVICE.md` - Full documentation
