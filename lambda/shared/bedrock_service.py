"""
Amazon Bedrock Service for HiveMind — Amazon Nova Edition
==========================================================
All AI calls use Amazon Nova models via the Converse and invoke_model APIs.

Models:
  Text/Reasoning → amazon.nova-2-lite-v1:0   (Converse API)
  Embeddings     → amazon.nova-2-multimodal-embeddings-v1:0  (invoke_model)
"""
import boto3
import json
import os
from typing import List, Optional, Dict, Any
from botocore.config import Config
import hashlib

# ---------------------------------------------------------------------------
# Bedrock client
# ---------------------------------------------------------------------------
bedrock_config = Config(
    region_name=os.environ.get('AWS_REGION', 'us-east-1'),
    retries={'max_attempts': 3, 'mode': 'adaptive'},
    read_timeout=300,
    connect_timeout=60,
)

bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    config=bedrock_config,
)

# ---------------------------------------------------------------------------
# Nova Model IDs
# ---------------------------------------------------------------------------
EMBEDDING_MODEL = os.environ.get(
    'NOVA_EMBEDDING_MODEL', 'amazon.nova-2-multimodal-embeddings-v1:0'
)
TEXT_MODEL = os.environ.get(
    'NOVA_TEXT_MODEL', 'amazon.nova-2-lite-v1:0'
)
EMBEDDING_DIMENSION = int(os.environ.get('NOVA_EMBEDDING_DIMENSION', '1024'))


class BedrockService:
    """Service for Amazon Bedrock AI operations using Nova models."""

    def __init__(self, cache_client=None):
        self.bedrock = bedrock_runtime
        self.cache = cache_client
        self.embedding_dimension = EMBEDDING_DIMENSION

    # ------------------------------------------------------------------
    # Embeddings  (Nova Multimodal Embeddings via invoke_model)
    # ------------------------------------------------------------------
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using Amazon Nova Multimodal Embeddings."""
        if not text or not text.strip():
            return [0.0] * self.embedding_dimension

        if self.cache:
            cache_key = f"nova:emb:{hashlib.sha256(text.encode()).hexdigest()}"
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached

        try:
            response = self.bedrock.invoke_model(
                modelId=EMBEDDING_MODEL,
                body=json.dumps({
                    'input': text,
                    'inputText': text,
                    'taskType': 'SINGLE_EMBEDDING',
                    'embeddingConfig': {
                        'outputEmbeddingLength': self.embedding_dimension,
                    },
                }),
            )
            result = json.loads(response['body'].read())
            embedding = result['embedding']

            if self.cache:
                self._set_cache(cache_key, embedding, ttl=86400)

            return embedding

        except Exception as e:
            print(f"Nova embedding error: {e}")
            return [0.0] * self.embedding_dimension

    def generate_batch_embeddings(
        self, texts: List[str], batch_size: int = 25
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        return [self.generate_embedding(t) for t in texts]

    # ------------------------------------------------------------------
    # Text generation  (Nova 2 Lite via Converse API)
    # ------------------------------------------------------------------
    def generate_text(
        self,
        prompt: str,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate text using Amazon Nova 2 Lite via the Converse API."""
        model_id = model or TEXT_MODEL

        try:
            kwargs: Dict[str, Any] = {
                'modelId': model_id,
                'messages': [
                    {'role': 'user', 'content': [{'text': prompt}]}
                ],
                'inferenceConfig': {
                    'temperature': temperature,
                    'maxTokens': max_tokens,
                },
            }
            if system_prompt:
                kwargs['system'] = [{'text': system_prompt}]

            response = self.bedrock.converse(**kwargs)
            output_msg = response['output']['message']
            content = output_msg['content'][0]['text']
            usage = response.get('usage', {})

            return {
                'content': content,
                'usage': {
                    'input_tokens': usage.get('inputTokens', 0),
                    'output_tokens': usage.get('outputTokens', 0),
                },
                'model': model_id,
            }

        except Exception as e:
            print(f"Nova text generation error: {e}")
            return {
                'content': '',
                'usage': {'input_tokens': 0, 'output_tokens': 0},
                'error': str(e),
            }

    # ------------------------------------------------------------------
    # Cache helpers
    # ------------------------------------------------------------------
    def _get_from_cache(self, key: str) -> Optional[List[float]]:
        if not self.cache:
            return None
        try:
            import asyncio
            cached = asyncio.run(self.cache.get(key))
            if cached:
                return json.loads(cached)
        except Exception:
            pass
        return None

    def _set_cache(self, key: str, value: List[float], ttl: int):
        if not self.cache:
            return
        try:
            import asyncio
            asyncio.run(self.cache.setex(key, ttl, json.dumps(value)))
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
_bedrock_service = None


def get_bedrock_service(cache_client=None) -> BedrockService:
    """Get or create BedrockService singleton."""
    global _bedrock_service
    if _bedrock_service is None:
        _bedrock_service = BedrockService(cache_client)
    return _bedrock_service


# ---------------------------------------------------------------------------
# Convenience functions (backward-compatible)
# ---------------------------------------------------------------------------
def generate_embedding(text: str) -> List[float]:
    """Generate embedding using Nova Multimodal Embeddings."""
    return get_bedrock_service().generate_embedding(text)


def generate_batch_embeddings(texts: List[str], batch_size: int = 25) -> List[List[float]]:
    """Generate batch embeddings using Nova Multimodal Embeddings."""
    return get_bedrock_service().generate_batch_embeddings(texts, batch_size)


def generate_text(
    prompt: str,
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> str:
    """Generate text using Nova 2 Lite and return the content string."""
    result = get_bedrock_service().generate_text(prompt, model, temperature, max_tokens)
    return result.get('content', '')
