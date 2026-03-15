# Vector DB Verification (Nova)

## Expected State

- All production embedding vectors are `1024` dimensions.
- Runtime model is `amazon.nova-2-multimodal-embeddings-v1:0`.
- Similarity queries use pgvector cosine operators.

## Verification SQL

```sql
-- pgvector extension exists
SELECT * FROM pg_extension WHERE extname = 'vector';

-- vector columns
SELECT table_name, column_name, udt_name
FROM information_schema.columns
WHERE udt_name = 'vector'
ORDER BY table_name, column_name;
```

## Runtime Checks

1. Generate embedding and confirm `len(vector) == 1024`.
2. Insert vector into each target table and run similarity query.
3. Validate top-k retrieval returns expected rows.
4. Verify no runtime model IDs reference Titan/Claude.

## Lambda/Service Checks

- `backend-aws/lambda/*` handlers generate embeddings via Nova model ID.
- `backend-aws/lambda-microservices/services/aws_ai_service.py` returns 1024-dim vectors.
- `lambda/shared/bedrock_service.py` and `backend/ai/bedrock_nova_client.py` use consistent payloads.

## Pass Criteria

- No embedding dimension mismatch errors
- No Bedrock validation errors from payload format
- ANN index queries remain performant
- Output vectors are consistently non-empty for non-empty input
