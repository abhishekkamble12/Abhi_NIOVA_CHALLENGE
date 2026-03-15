"""Amazon Nova AI Service for HiveMind"""
from .bedrock_nova_client import (
    NovaClient,
    get_nova_client,
    generate_text,
    summarize_text,
    generate_embeddings,
    generate_multimodal_embedding,
    analyze_content,
    transcribe_audio,
)

__all__ = [
    "NovaClient",
    "get_nova_client",
    "generate_text",
    "summarize_text",
    "generate_embeddings",
    "generate_multimodal_embedding",
    "analyze_content",
    "transcribe_audio",
]
