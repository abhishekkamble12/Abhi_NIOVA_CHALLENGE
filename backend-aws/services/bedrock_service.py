"""
Bedrock Service for EC2 — Amazon Nova Edition
===============================================
Uses Amazon Nova models via HTTP Bedrock Runtime endpoints.

Models:
  Text/Reasoning → amazon.nova-2-lite-v1:0   (Converse API)
  Embeddings     → amazon.nova-2-multimodal-embeddings-v1:0
"""
import json
import httpx
from typing import List
from aws_requests_auth.aws_auth import AWSRequestsAuth
from config.aws_config import get_aws_settings

settings = get_aws_settings()


class BedrockService:
    def __init__(self):
        self.region = settings.AWS_REGION
        self.endpoint = f"https://bedrock-runtime.{self.region}.amazonaws.com"
        self.model_embedding = settings.BEDROCK_MODEL_EMBEDDING
        self.model_text = settings.BEDROCK_MODEL_TEXT

        self.auth = AWSRequestsAuth(
            aws_access_key=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_host=f"bedrock-runtime.{self.region}.amazonaws.com",
            aws_region=self.region,
            aws_service='bedrock',
        )

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using Amazon Nova Multimodal Embeddings."""
        url = f"{self.endpoint}/model/{self.model_embedding}/invoke"
        payload = {
            "input": text,
            "inputText": text,
            "taskType": "SINGLE_EMBEDDING",
            "embeddingConfig": {
                "outputEmbeddingLength": 1024,
            },
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                auth=self.auth,
            )
            response.raise_for_status()
            result = response.json()
            return result.get("embedding", [])

    async def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate multiple embeddings."""
        return [await self.generate_embedding(text) for text in texts]

    async def generate_text(
        self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7
    ) -> str:
        """Generate text using Amazon Nova 2 Lite via the Converse API."""
        url = f"{self.endpoint}/model/{self.model_text}/converse"

        payload = {
            "messages": [
                {"role": "user", "content": [{"text": prompt}]}
            ],
            "inferenceConfig": {
                "temperature": temperature,
                "maxTokens": max_tokens,
            },
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                auth=self.auth,
            )
            response.raise_for_status()
            result = response.json()
            return (
                result.get("output", {})
                .get("message", {})
                .get("content", [{}])[0]
                .get("text", "")
            )


def get_bedrock_service() -> BedrockService:
    return BedrockService()
