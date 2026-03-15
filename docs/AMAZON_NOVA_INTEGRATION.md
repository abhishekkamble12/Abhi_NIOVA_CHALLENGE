# Amazon Nova Integration

This repository standardizes all Bedrock AI operations on the Amazon Nova model family.

## Models

- **Text / Reasoning / Analysis**: `amazon.nova-2-lite-v1:0`
- **Speech / Voice**: `amazon.nova-2-sonic-v1:0`
- **Embeddings / Retrieval**: `amazon.nova-2-multimodal-embeddings-v1:0`

## APIs

- `converse()` for reasoning and generation tasks
- `invoke_model()` for embedding generation
- `start_async_invoke()` for long-running and batch embedding workflows

## Central Client

Use `backend/ai/bedrock_nova_client.py` from backend services whenever possible.

## Multimodal Block Example

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

For the full migration and file-level changes, see `NOVA_INTEGRATION.md`.
