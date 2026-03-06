"""
Amazon Bedrock Service for HiveMind
Replaces SentenceTransformers with Bedrock APIs
"""
import boto3
import json
import os
from typing import List, Optional, Dict, Any
from botocore.config import Config
import hashlib

# Configure Bedrock client with retry logic
bedrock_config = Config(
    region_name=os.environ.get('AWS_REGION', 'us-east-1'),
    retries={
        'max_attempts': 3,
        'mode': 'adaptive'
    },
    read_timeout=300,
    connect_timeout=60
)

# Initialize Bedrock client
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    config=bedrock_config
)

# Model IDs
EMBEDDING_MODEL = 'amazon.titan-embed-text-v1'
TEXT_MODEL_FAST = 'amazon.titan-text-express-v1'
TEXT_MODEL_ADVANCED = 'anthropic.claude-3-sonnet-20240229-v1:0'
TEXT_MODEL_BUDGET = 'anthropic.claude-3-haiku-20240307-v1:0'


class BedrockService:
    """
    Service for Amazon Bedrock AI operations
    """
    
    def __init__(self, cache_client=None):
        """
        Initialize Bedrock service
        
        Args:
            cache_client: Optional Redis client for caching
        """
        self.bedrock = bedrock_runtime
        self.cache = cache_client
        self.embedding_dimension = 1536  # Titan embeddings dimension
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding using Bedrock Titan Embeddings
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            return [0.0] * self.embedding_dimension
        
        # Check cache
        if self.cache:
            cache_key = f"bedrock:emb:{hashlib.sha256(text.encode()).hexdigest()}"
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached
        
        # Generate embedding with Bedrock
        try:
            response = self.bedrock.invoke_model(
                modelId=EMBEDDING_MODEL,
                body=json.dumps({
                    'inputText': text
                })
            )
            
            result = json.loads(response['body'].read())
            embedding = result['embedding']
            
            # Cache result
            if self.cache:
                self._set_cache(cache_key, embedding, ttl=86400)  # 24 hours
            
            return embedding
        
        except Exception as e:
            print(f"Bedrock embedding error: {str(e)}")
            # Return zero vector on error
            return [0.0] * self.embedding_dimension
    
    def generate_batch_embeddings(
        self,
        texts: List[str],
        batch_size: int = 25
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Note: Bedrock doesn't have native batch API, so we process sequentially
        
        Args:
            texts: List of texts to embed
            batch_size: Not used (kept for compatibility)
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for text in texts:
            embedding = self.generate_embedding(text)
            embeddings.append(embedding)
        
        return embeddings
    
    def generate_text(
        self,
        prompt: str,
        model: str = TEXT_MODEL_FAST,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate text using Bedrock LLMs
        
        Args:
            prompt: User prompt
            model: Model ID (titan-text, claude-3-sonnet, claude-3-haiku)
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt
            
        Returns:
            Dict with 'content' and 'usage' keys
        """
        try:
            if 'claude' in model:
                return self._generate_claude(prompt, model, temperature, max_tokens, system_prompt)
            else:
                return self._generate_titan(prompt, model, temperature, max_tokens)
        
        except Exception as e:
            print(f"Bedrock text generation error: {str(e)}")
            return {
                'content': '',
                'usage': {'input_tokens': 0, 'output_tokens': 0},
                'error': str(e)
            }
    
    def _generate_claude(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """
        Generate text using Claude models
        """
        messages = [{'role': 'user', 'content': prompt}]
        
        body = {
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': max_tokens,
            'temperature': temperature,
            'messages': messages
        }
        
        if system_prompt:
            body['system'] = system_prompt
        
        response = self.bedrock.invoke_model(
            modelId=model,
            body=json.dumps(body)
        )
        
        result = json.loads(response['body'].read())
        
        return {
            'content': result['content'][0]['text'],
            'usage': {
                'input_tokens': result.get('usage', {}).get('input_tokens', 0),
                'output_tokens': result.get('usage', {}).get('output_tokens', 0)
            },
            'model': model
        }
    
    def _generate_titan(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """
        Generate text using Titan models
        """
        body = {
            'inputText': prompt,
            'textGenerationConfig': {
                'maxTokenCount': max_tokens,
                'temperature': temperature,
                'topP': 0.9
            }
        }
        
        response = self.bedrock.invoke_model(
            modelId=model,
            body=json.dumps(body)
        )
        
        result = json.loads(response['body'].read())
        
        return {
            'content': result['results'][0]['outputText'],
            'usage': {
                'input_tokens': result.get('inputTextTokenCount', 0),
                'output_tokens': result['results'][0].get('tokenCount', 0)
            },
            'model': model
        }
    
    def _get_from_cache(self, key: str) -> Optional[List[float]]:
        """Get embedding from cache"""
        if not self.cache:
            return None
        
        try:
            import asyncio
            cached = asyncio.run(self.cache.get(key))
            if cached:
                return json.loads(cached)
        except:
            pass
        
        return None
    
    def _set_cache(self, key: str, value: List[float], ttl: int):
        """Set embedding in cache"""
        if not self.cache:
            return
        
        try:
            import asyncio
            asyncio.run(self.cache.setex(key, ttl, json.dumps(value)))
        except:
            pass


# Global instance
_bedrock_service = None


def get_bedrock_service(cache_client=None) -> BedrockService:
    """
    Get or create Bedrock service instance (singleton)
    """
    global _bedrock_service
    
    if _bedrock_service is None:
        _bedrock_service = BedrockService(cache_client)
    
    return _bedrock_service


# Convenience functions for backward compatibility
def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding using Bedrock
    
    Drop-in replacement for SentenceTransformers
    """
    service = get_bedrock_service()
    return service.generate_embedding(text)


def generate_batch_embeddings(texts: List[str], batch_size: int = 25) -> List[List[float]]:
    """
    Generate embeddings for multiple texts
    
    Drop-in replacement for SentenceTransformers
    """
    service = get_bedrock_service()
    return service.generate_batch_embeddings(texts, batch_size)


def generate_text(
    prompt: str,
    model: str = TEXT_MODEL_FAST,
    temperature: float = 0.7,
    max_tokens: int = 1024
) -> str:
    """
    Generate text using Bedrock
    
    Returns just the content string for simplicity
    """
    service = get_bedrock_service()
    result = service.generate_text(prompt, model, temperature, max_tokens)
    return result.get('content', '')
