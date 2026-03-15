# Amazon Nova Quick Reference

## Model Mapping

- **Text / Reasoning / Analysis**: `amazon.nova-2-lite-v1:0` (or `us.amazon.nova-lite-v1:0`)
- **Speech / Voice**: `amazon.nova-2-sonic-v1:0`
- **Embeddings / Vector Search**: `amazon.nova-2-multimodal-embeddings-v1:0`

## Bedrock Client Setup

```python
import boto3
from botocore.config import Config

cfg = Config(
    region_name="us-east-1",
    retries={"max_attempts": 3, "mode": "adaptive"},
    read_timeout=120,
    connect_timeout=30,
)
bedrock = boto3.client("bedrock-runtime", config=cfg)
```

## Text Generation (Converse API)

```python
response = bedrock.converse(
    modelId="amazon.nova-2-lite-v1:0",
    messages=[{
        "role": "user",
        "content": [{"text": "Write a LinkedIn post about GenAI trends"}]
    }],
    inferenceConfig={
        "temperature": 0.7,
        "maxTokens": 1024
    }
)
text = response["output"]["message"]["content"][0]["text"]
```

## Embedding Generation (invoke_model)

```python
import json

response = bedrock.invoke_model(
    modelId="amazon.nova-2-multimodal-embeddings-v1:0",
    body=json.dumps({
        "input": "AI trends in social media",
        "inputText": "AI trends in social media",
        "taskType": "SINGLE_EMBEDDING",
        "embeddingConfig": {"outputEmbeddingLength": 1024}
    })
)
embedding = json.loads(response["body"].read())["embedding"]  # 1024-dim
```

## Multimodal Input Block (Image + Text)

```json
{
  "role": "user",
  "content": [
    {"text": "Describe this image for a social caption."},
    {
      "image": {
        "format": "jpeg",
        "source": {"bytes": "<base64-bytes>"}
      }
    }
  ]
}
```

## Async Invocation (Long-running Embedding/Batch Jobs)

```python
job = bedrock.start_async_invoke(
    modelId="amazon.nova-2-multimodal-embeddings-v1:0",
    modelInput={
        "input": "very large batch payload",
        "taskType": "SINGLE_EMBEDDING"
    },
    outputDataConfig={
        "s3OutputDataConfig": {"s3Uri": "s3://your-bucket/bedrock-output/"}
    }
)
```

## pgvector Dimension

- Use `vector(1024)` for all Nova embedding columns.
- Rebuild ANN indexes after migrating dimensions.

## Environment Variables

```bash
AWS_REGION=us-east-1
NOVA_TEXT_MODEL=amazon.nova-2-lite-v1:0
NOVA_SONIC_MODEL=amazon.nova-2-sonic-v1:0
NOVA_EMBEDDING_MODEL=amazon.nova-2-multimodal-embeddings-v1:0
NOVA_EMBEDDING_DIMENSION=1024
```

## IAM Permissions

```json
{
  "Effect": "Allow",
  "Action": ["bedrock:InvokeModel", "bedrock:Converse", "bedrock:StartAsyncInvoke"],
  "Resource": [
    "arn:aws:bedrock:*::foundation-model/amazon.nova-2-lite-v1:0",
    "arn:aws:bedrock:*::foundation-model/amazon.nova-2-sonic-v1:0",
    "arn:aws:bedrock:*::foundation-model/amazon.nova-2-multimodal-embeddings-v1:0"
  ]
}
```
