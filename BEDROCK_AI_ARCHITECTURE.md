# Amazon Nova AI Architecture

## Executive Summary

HiveMind uses AWS Bedrock with the Amazon Nova model family:

- **Nova 2 Lite** for reasoning, summarization, content generation, trend analysis
- **Nova 2 Sonic** for speech/voice workflows (roadmap + staged rollout)
- **Nova Multimodal Embeddings** for semantic search and retrieval (`pgvector`)

## Core AI Flow

1. User request arrives (social/news/video module)
2. Query is embedded with Nova Multimodal Embeddings (`1024` dim)
3. Similar content is retrieved from PostgreSQL + pgvector / OpenSearch
4. Context is assembled
5. Nova 2 Lite generates response through `converse()`
6. Output is stored with metadata and embedding for future learning

## Bedrock API Strategy

- **Reasoning / generation**: `client.converse(...)`
- **Embeddings**: `client.invoke_model(...)`
- **Long-running / batch embedding jobs**: `client.start_async_invoke(...)`

## Canonical Model IDs

```yaml
text_reasoning: amazon.nova-2-lite-v1:0
speech_voice: amazon.nova-2-sonic-v1:0
embeddings: amazon.nova-2-multimodal-embeddings-v1:0
```

If region compatibility requires a prefix, use `us.amazon.nova-lite-v1:0` for text.

## Standard Payloads

### Converse (Text)

```python
response = bedrock.converse(
    modelId="amazon.nova-2-lite-v1:0",
    messages=[{
        "role": "user",
        "content": [{"text": prompt}]
    }],
    inferenceConfig={"temperature": 0.7, "maxTokens": 1024}
)
```

### Embeddings

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
```

### Multimodal Image Input

```json
{
  "type": "image",
  "source": {
    "type": "base64",
    "media_type": "image/jpeg",
    "data": "<base64>"
  }
}
```

## Data Layer

- `articles.embedding` → `vector(1024)`
- `generated_posts.embedding` → `vector(1024)`
- `video_scenes.embedding` → `vector(1024)`
- `user_interest_embeddings.embedding` → `vector(1024)`

Index strategy:

- IVFFlat for ANN search
- cosine similarity (`<=>`) in pgvector queries

## Central AI Service

All backend AI calls route through:

- `backend/ai/bedrock_nova_client.py`

Exposed helpers:

- `generate_text(prompt)`
- `summarize_text(text)`
- `generate_embeddings(text)`
- `generate_multimodal_embedding(...)`
- `analyze_content(prompt)`
- `transcribe_audio(audio)`

## Validation Checklist

- Bedrock runtime clients initialize with explicit region + retry config
- No Titan/Claude model IDs in runtime code paths
- `converse()` used for text reasoning workflows
- Embeddings are stored and queried as `vector(1024)`
- Lambda handlers still preserve business logic and event contracts
- Streaming compatibility plan documented (`converse_stream` when enabled)

## Known Limits / TODO

1. Nova 2 Sonic speech-input workflow is scaffolded; AWS Transcribe remains active for production transcription.
2. Some legacy docs in nested folders may still describe historical Titan/Claude architecture; prefer this file + `NOVA_INTEGRATION.md`.
3. For very large embedding batches, move sequential embedding loops to `start_async_invoke` jobs with S3 output.
