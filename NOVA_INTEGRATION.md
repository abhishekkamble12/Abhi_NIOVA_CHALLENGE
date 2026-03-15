# Amazon Nova Integration Guide

## Overview

All AI operations in HiveMind are powered by **Amazon Nova** foundation models via AWS Bedrock. This document describes the model mapping, API patterns, and migration notes.

---

## Model Mapping

| Use Case | Model ID | Bedrock API | Dimension |
|---|---|---|---|
| Text generation, summarization, content analysis, social post creation, NLP tagging, performance insights | `amazon.nova-2-lite-v1:0` | `converse()` | — |
| Voice input/output, speech-to-text, audio understanding | `amazon.nova-2-sonic-v1:0` | `converse()` | — |
| Semantic search, pgvector storage, recommendations, article similarity, multimodal retrieval | `amazon.nova-2-multimodal-embeddings-v1:0` | `invoke_model()` | 1024 |

> For regions that require a cross-region prefix, use `us.amazon.nova-lite-v1:0` instead.

---

## API Patterns

### Text / Reasoning (Converse API)

```python
import boto3, json

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

response = bedrock.converse(
    modelId="amazon.nova-2-lite-v1:0",
    messages=[
        {"role": "user", "content": [{"text": "Summarize this article..."}]}
    ],
    system=[{"text": "You are a concise summarization assistant."}],
    inferenceConfig={
        "temperature": 0.7,
        "maxTokens": 1024,
    },
)

text = response["output"]["message"]["content"][0]["text"]
usage = response["usage"]  # {"inputTokens": ..., "outputTokens": ...}
```

### Embeddings (invoke_model)

```python
response = bedrock.invoke_model(
    modelId="amazon.nova-2-multimodal-embeddings-v1:0",
    body=json.dumps({
        "inputText": "content to embed",
        "embeddingConfig": {
            "outputEmbeddingLength": 1024,
        },
    }),
)
result = json.loads(response["body"].read())
embedding = result["embedding"]  # List[float], length 1024
```

### Multimodal Embedding (text + image)

```python
import base64

with open("image.jpg", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode()

response = bedrock.invoke_model(
    modelId="amazon.nova-2-multimodal-embeddings-v1:0",
    body=json.dumps({
        "inputText": "optional text description",
        "inputImage": image_b64,
        "embeddingConfig": {"outputEmbeddingLength": 1024},
    }),
)
```

### Async / Batch (start_async_invoke)

For long-running video or batch embedding jobs:

```python
response = bedrock.start_async_invoke(
    modelId="amazon.nova-2-multimodal-embeddings-v1:0",
    modelInput={...},
    outputDataConfig={"s3OutputDataConfig": {"s3Uri": "s3://bucket/output/"}},
)
invocation_arn = response["invocationArn"]
```

---

## Central AI Service

All application modules call `backend/ai/bedrock_nova_client.py` instead of directly invoking Bedrock:

| Function | Purpose |
|---|---|
| `generate_text(prompt)` | General text generation (Nova 2 Lite) |
| `summarize_text(text)` | Concise summarization |
| `generate_embeddings(text)` | 1024-dim text embedding |
| `generate_multimodal_embedding(text, image_base64)` | Joint text+image embedding |
| `analyze_content(prompt)` | Content/performance analysis |
| `transcribe_audio(audio_bytes)` | Speech input (Nova 2 Sonic placeholder) |

---

## File-by-File Changes

### Core services (direct Bedrock calls)

| File | Before | After |
|---|---|---|
| `lambda/shared/bedrock_service.py` | Titan Embed v1 + Claude 3 Sonnet/Haiku + Titan Text Express | Nova Multimodal Embeddings + Nova 2 Lite (Converse) |
| `backend-aws/services/bedrock_service.py` | Titan Embed v2 + Claude 3 Sonnet (HTTP) | Nova Multimodal Embeddings + Nova 2 Lite (HTTP Converse) |
| `backend-aws/lambda-microservices/services/aws_ai_service.py` | Titan Embed v1 + Claude 3 Sonnet | Nova Multimodal Embeddings + Nova 2 Lite (Converse) |
| `backend/app/ai-engine/context.py` | Nova Lite v1 (invoke_model) | Nova 2 Lite (Converse API) |
| `backend/app/services/vector_service.py` | SentenceTransformer (all-MiniLM-L6-v2, 384-dim) | Nova Multimodal Embeddings (1024-dim) |
| `backend/app/api/v1/et/backend/services_news_feed.py` | OpenAI GPT-4 + ada-002 | Nova 2 Lite + Nova Multimodal Embeddings |

### Lambda handlers

| File | Before | After |
|---|---|---|
| `backend-aws/lambda/article_created_handler.py` | Titan Embed v2 + Claude 3 Sonnet | Nova Embeddings + Nova 2 Lite (Converse) |
| `backend-aws/lambda/video_uploaded_handler.py` | Titan Embed v2 | Nova Multimodal Embeddings |
| `backend-aws/lambda/post_engagement_handler.py` | Claude 3 Sonnet | Nova 2 Lite (Converse) |

### Configuration

| File | Change |
|---|---|
| `backend-aws/config/aws_config.py` | Default models → Nova |
| `backend/app/core/config.py` | `VECTOR_DIMENSION=1024`, `EMBEDDING_MODEL=amazon.nova-2-multimodal-embeddings-v1:0` |
| `backend-aws/.env.example` | Nova model IDs |
| `backend/.env.example` | Nova model IDs, removed OpenAI dependency |
| `db-setup/schema_vector.sql` | `vector(384)` → `vector(1024)` everywhere |
| `db-setup/migrate_to_vector.py` | SentenceTransformer → Bedrock Nova invoke_model |

---

## Database Migration Notes

The embedding dimension changed from **384** (MiniLM) / **1536** (Titan/OpenAI) to **1024** (Nova).

If you have existing vectors in pgvector, you must:

1. Alter the vector column size: `ALTER TABLE articles ALTER COLUMN embedding TYPE vector(1024);`
2. Re-generate all embeddings using the migration script: `python db-setup/migrate_to_vector.py`
3. Rebuild IVFFlat indexes after migration.

---

## Environment Variables

```bash
NOVA_TEXT_MODEL=amazon.nova-2-lite-v1:0
NOVA_SONIC_MODEL=amazon.nova-2-sonic-v1:0
NOVA_EMBEDDING_MODEL=amazon.nova-2-multimodal-embeddings-v1:0
NOVA_EMBEDDING_DIMENSION=1024
AWS_REGION=us-east-1
```

---

## TODO / Known Limitations

1. **Nova 2 Sonic speech input** — The `transcribe_audio()` function in `bedrock_nova_client.py` is a placeholder. Nova 2 Sonic speech-to-text is awaiting GA. Currently, audio transcription continues to use AWS Transcribe.

2. **Cross-region model IDs** — Some regions may require the `us.amazon.nova-*` prefix instead of `amazon.nova-*`. Set the `NOVA_TEXT_MODEL` / `NOVA_EMBEDDING_MODEL` environment variables accordingly.

3. **Batch embedding API** — Nova Multimodal Embeddings does not have a native batch endpoint. The code processes texts sequentially. For large batch jobs, consider using `start_async_invoke()`.

4. **Image/video understanding** — Nova 2 Lite supports multimodal content blocks (images). Image analysis currently uses Rekognition. A future enhancement can send images directly to Nova 2 Lite via content blocks:
   ```python
   {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": "<base64>"}}
   ```

5. **Streaming** — The Converse API supports `converse_stream()` for token-level streaming. This is not yet wired into the application but is a drop-in replacement for `converse()`.
