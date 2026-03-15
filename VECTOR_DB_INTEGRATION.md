# Vector DB Integration (Nova Embeddings)

## Overview

The platform now uses **Amazon Nova Multimodal Embeddings** as the canonical vector generator.
All vectors are normalized to **1024 dimensions** and persisted in `pgvector`.

## Database Schema

Updated vector columns:

- `articles.embedding vector(1024)`
- `generated_posts.embedding vector(1024)`
- `video_scenes.embedding vector(1024)`
- `user_interest_embeddings.embedding vector(1024)`

## Embedding API Standard

```python
response = bedrock.invoke_model(
    modelId="amazon.nova-2-multimodal-embeddings-v1:0",
    body=json.dumps({
        "input": text,
        "inputText": text,
        "taskType": "SINGLE_EMBEDDING",
        "embeddingConfig": {"outputEmbeddingLength": 1024}
    })
)
vector = json.loads(response["body"].read())["embedding"]
```

## Migration Notes

1. Alter vector column dimensions to `1024`.
2. Recompute existing vectors using Nova.
3. Rebuild IVFFlat indexes after migration.
4. Validate retrieval quality and latency.

## Query Pattern

```sql
SELECT id, 1 - (embedding <=> :query_embedding) AS similarity
FROM articles
WHERE embedding IS NOT NULL
ORDER BY embedding <=> :query_embedding
LIMIT 10;
```

## Operational Guidance

- Keep a cache layer for repeated embedding requests.
- Use async jobs (`start_async_invoke`) for large offline/batch embedding workloads.
- Track embedding generation failures and fallback to zero vectors only as last resort.
