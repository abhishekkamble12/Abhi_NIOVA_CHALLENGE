"""
Central Amazon Nova AI Service for HiveMind
============================================
All AI operations route through this module.

Models:
  - Text/Reasoning/Analysis → Amazon Nova 2 Lite  (converse API)
  - Speech/Voice            → Amazon Nova 2 Sonic  (converse API)
  - Embeddings/Vectors      → Amazon Nova Multimodal Embeddings (invoke_model)
"""
import boto3
import json
import os
import hashlib
from typing import List, Optional, Dict, Any
from botocore.config import Config

# ---------------------------------------------------------------------------
# Nova Model IDs
# ---------------------------------------------------------------------------
NOVA_TEXT_MODEL = os.environ.get(
    "NOVA_TEXT_MODEL", "amazon.nova-2-lite-v1:0"
)
NOVA_SONIC_MODEL = os.environ.get(
    "NOVA_SONIC_MODEL", "amazon.nova-2-sonic-v1:0"
)
NOVA_EMBEDDING_MODEL = os.environ.get(
    "NOVA_EMBEDDING_MODEL", "amazon.nova-2-multimodal-embeddings-v1:0"
)

NOVA_EMBEDDING_DIMENSION = int(os.environ.get("NOVA_EMBEDDING_DIMENSION", "1024"))

# ---------------------------------------------------------------------------
# Bedrock client configuration
# ---------------------------------------------------------------------------
_bedrock_config = Config(
    region_name=os.environ.get("AWS_REGION", "us-east-1"),
    retries={"max_attempts": 3, "mode": "adaptive"},
    read_timeout=300,
    connect_timeout=60,
)

_bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    config=_bedrock_config,
)


class NovaClient:
    """Unified client for all Amazon Nova operations on Bedrock."""

    def __init__(self, client=None, cache_client=None):
        self.bedrock = client or _bedrock_runtime
        self.cache = cache_client
        self.embedding_dimension = NOVA_EMBEDDING_DIMENSION

    # ------------------------------------------------------------------
    # TEXT / REASONING  (Converse API → Nova 2 Lite)
    # ------------------------------------------------------------------
    def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate text using Amazon Nova 2 Lite via the Converse API."""
        messages = [
            {"role": "user", "content": [{"text": prompt}]}
        ]
        kwargs: Dict[str, Any] = {
            "modelId": NOVA_TEXT_MODEL,
            "messages": messages,
            "inferenceConfig": {
                "temperature": temperature,
                "maxTokens": max_tokens,
            },
        }
        if system_prompt:
            kwargs["system"] = [{"text": system_prompt}]

        try:
            response = self.bedrock.converse(**kwargs)
            output_message = response["output"]["message"]
            content = output_message["content"][0]["text"]
            usage = response.get("usage", {})
            return {
                "content": content,
                "usage": {
                    "input_tokens": usage.get("inputTokens", 0),
                    "output_tokens": usage.get("outputTokens", 0),
                },
                "model": NOVA_TEXT_MODEL,
            }
        except Exception as e:
            return {
                "content": "",
                "usage": {"input_tokens": 0, "output_tokens": 0},
                "error": str(e),
            }

    def summarize_text(
        self,
        text: str,
        max_tokens: int = 300,
        temperature: float = 0.3,
    ) -> Dict[str, Any]:
        """Summarize text using Nova 2 Lite."""
        system = "You are a precise summarization assistant. Provide concise summaries."
        prompt = f"Summarize the following text in 2-3 sentences:\n\n{text}"
        return self.generate_text(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system,
        )

    def analyze_content(
        self,
        prompt: str,
        temperature: float = 0.5,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """Analyse content (performance, trends, insights) using Nova 2 Lite."""
        system = (
            "You are an expert content analyst. "
            "Extract actionable insights from the data provided."
        )
        return self.generate_text(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system,
        )

    # ------------------------------------------------------------------
    # EMBEDDINGS  (invoke_model → Nova Multimodal Embeddings)
    # ------------------------------------------------------------------
    def generate_embeddings(self, text: str) -> List[float]:
        """Generate a text embedding using Amazon Nova Multimodal Embeddings."""
        if not text or not text.strip():
            return [0.0] * self.embedding_dimension

        if self.cache:
            cache_key = f"nova:emb:{hashlib.sha256(text.encode()).hexdigest()}"
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached

        try:
            body = json.dumps({
                "input": text,
                "inputText": text,
                "taskType": "SINGLE_EMBEDDING",
                "embeddingConfig": {
                    "outputEmbeddingLength": self.embedding_dimension,
                },
            })
            response = self.bedrock.invoke_model(
                modelId=NOVA_EMBEDDING_MODEL,
                body=body,
            )
            result = json.loads(response["body"].read())
            embedding = result["embedding"]

            if self.cache:
                self._set_cache(cache_key, embedding, ttl=86400)

            return embedding
        except Exception as e:
            print(f"Nova embedding error: {e}")
            return [0.0] * self.embedding_dimension

    def generate_batch_embeddings(
        self, texts: List[str], batch_size: int = 25
    ) -> List[List[float]]:
        """Generate embeddings for a list of texts sequentially."""
        return [self.generate_embeddings(t) for t in texts]

    def generate_multimodal_embedding(
        self,
        *,
        text: Optional[str] = None,
        image_base64: Optional[str] = None,
        image_media_type: str = "image/jpeg",
    ) -> List[float]:
        """Generate a multimodal embedding (text and/or image)."""
        body: Dict[str, Any] = {
            "embeddingConfig": {
                "outputEmbeddingLength": self.embedding_dimension,
            },
        }
        if text:
            body["input"] = text
            body["inputText"] = text
            body["taskType"] = "SINGLE_EMBEDDING"
        if image_base64:
            body["inputImage"] = image_base64

        try:
            response = self.bedrock.invoke_model(
                modelId=NOVA_EMBEDDING_MODEL,
                body=json.dumps(body),
            )
            result = json.loads(response["body"].read())
            return result["embedding"]
        except Exception as e:
            print(f"Nova multimodal embedding error: {e}")
            return [0.0] * self.embedding_dimension

    def start_async_embedding_job(
        self,
        *,
        text: str,
        output_s3_uri: str,
    ) -> Dict[str, Any]:
        """Start async embedding generation for large/batch workloads."""
        model_input = {
            "input": text,
            "inputText": text,
            "taskType": "SINGLE_EMBEDDING",
            "embeddingConfig": {
                "outputEmbeddingLength": self.embedding_dimension,
            },
        }
        return self.bedrock.start_async_invoke(
            modelId=NOVA_EMBEDDING_MODEL,
            modelInput=model_input,
            outputDataConfig={
                "s3OutputDataConfig": {
                    "s3Uri": output_s3_uri,
                }
            },
        )

    # ------------------------------------------------------------------
    # SPEECH / VOICE  (Nova 2 Sonic — placeholder for future integration)
    # ------------------------------------------------------------------
    def transcribe_audio(self, audio_bytes: bytes) -> Dict[str, Any]:
        """Speech-to-text placeholder using Nova 2 Sonic.

        TODO: Nova 2 Sonic speech API integration.  Currently delegates to
        AWS Transcribe for production use.  Update when Nova 2 Sonic speech
        input is GA.
        """
        return {
            "text": "",
            "model": NOVA_SONIC_MODEL,
            "note": "Nova 2 Sonic speech input — awaiting GA. Use AWS Transcribe in the interim.",
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
_nova_client: Optional[NovaClient] = None


def get_nova_client(cache_client=None) -> NovaClient:
    """Return the global NovaClient singleton."""
    global _nova_client
    if _nova_client is None:
        _nova_client = NovaClient(cache_client=cache_client)
    return _nova_client


# ---------------------------------------------------------------------------
# Convenience functions (drop-in replacements for legacy helpers)
# ---------------------------------------------------------------------------
def generate_text(
    prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    system_prompt: Optional[str] = None,
) -> str:
    """Generate text and return the content string."""
    client = get_nova_client()
    result = client.generate_text(prompt, temperature, max_tokens, system_prompt)
    return result.get("content", "")


def summarize_text(text: str, max_tokens: int = 300) -> str:
    client = get_nova_client()
    result = client.summarize_text(text, max_tokens)
    return result.get("content", "")


def generate_embeddings(text: str) -> List[float]:
    """Generate embedding — drop-in replacement for legacy functions."""
    client = get_nova_client()
    return client.generate_embeddings(text)


def generate_multimodal_embedding(
    *,
    text: Optional[str] = None,
    image_base64: Optional[str] = None,
    image_media_type: str = "image/jpeg",
) -> List[float]:
    client = get_nova_client()
    return client.generate_multimodal_embedding(
        text=text, image_base64=image_base64, image_media_type=image_media_type
    )


def analyze_content(prompt: str, max_tokens: int = 1024) -> str:
    client = get_nova_client()
    result = client.analyze_content(prompt, max_tokens=max_tokens)
    return result.get("content", "")


def transcribe_audio(audio_bytes: bytes) -> Dict[str, Any]:
    client = get_nova_client()
    return client.transcribe_audio(audio_bytes)
