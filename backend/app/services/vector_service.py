"""
Vector Service — Amazon Nova Multimodal Embeddings Edition
===========================================================
Replaces SentenceTransformers with Bedrock Nova Multimodal Embeddings.
Embedding dimension: 1024 (Nova default).
"""
import boto3
import json
import os
import hashlib
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.core.config import settings
from app.core.logging import get_logger
from app.core.redis import cache_embeddings, get_cached_embeddings
from app.models import Article, GeneratedPost, VideoScene

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Bedrock client for Nova embeddings
# ---------------------------------------------------------------------------
from botocore.config import Config as BotoConfig

_bedrock_config = BotoConfig(
    region_name=os.environ.get('AWS_REGION', settings.AWS_REGION),
    retries={'max_attempts': 3, 'mode': 'adaptive'},
    read_timeout=120,
    connect_timeout=30,
)

_bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    config=_bedrock_config,
)

NOVA_EMBEDDING_MODEL = os.environ.get(
    'NOVA_EMBEDDING_MODEL', 'amazon.nova-2-multimodal-embeddings-v1:0'
)


class VectorService:
    """Service for generating and searching vector embeddings using Nova."""

    def __init__(self):
        self.dimension = settings.VECTOR_DIMENSION
        self.bedrock = _bedrock_runtime

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using Amazon Nova Multimodal Embeddings."""
        if not text or not text.strip():
            return [0.0] * self.dimension

        cache_key = hashlib.sha256(text.encode()).hexdigest()

        import asyncio
        try:
            cached = asyncio.run(get_cached_embeddings(cache_key))
            if cached:
                logger.debug(f"Cache hit for embedding: {cache_key[:8]}...")
                return cached
        except Exception:
            pass

        try:
            response = self.bedrock.invoke_model(
                modelId=NOVA_EMBEDDING_MODEL,
                body=json.dumps({
                    'input': text,
                    'inputText': text,
                    'taskType': 'SINGLE_EMBEDDING',
                    'embeddingConfig': {
                        'outputEmbeddingLength': self.dimension,
                    },
                }),
            )
            result = json.loads(response['body'].read())
            embedding = result['embedding']

            try:
                asyncio.run(cache_embeddings(cache_key, embedding, ttl=86400))
            except Exception:
                pass

            return embedding

        except Exception as e:
            logger.error(f"Nova embedding error: {e}")
            return [0.0] * self.dimension

    def generate_batch_embeddings(
        self, texts: List[str], batch_size: int = 32
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        if not texts:
            return []

        embeddings = [self.generate_embedding(t) for t in texts]
        logger.info(f"Generated {len(embeddings)} embeddings via Nova")
        return embeddings

    async def search_similar_articles(
        self,
        db: AsyncSession,
        query_text: str,
        limit: int = 10,
        min_similarity: float = 0.0,
    ) -> List[Tuple[Article, float]]:
        """Search for similar articles using semantic search."""
        query_embedding = self.generate_embedding(query_text)

        query = text("""
            SELECT id, title, content, url, source, category,
                   1 - (embedding <=> :query_embedding) AS similarity
            FROM articles
            WHERE embedding IS NOT NULL
              AND 1 - (embedding <=> :query_embedding) >= :min_similarity
            ORDER BY embedding <=> :query_embedding
            LIMIT :limit
        """)

        result = await db.execute(
            query,
            {
                "query_embedding": query_embedding,
                "min_similarity": min_similarity,
                "limit": limit,
            },
        )
        rows = result.fetchall()

        articles_with_similarity = []
        for row in rows:
            article_result = await db.execute(
                select(Article).filter(Article.id == row.id)
            )
            article = article_result.scalar_one_or_none()
            if article:
                articles_with_similarity.append((article, row.similarity))

        logger.info(f"Found {len(articles_with_similarity)} similar articles")
        return articles_with_similarity

    async def search_similar_posts(
        self,
        db: AsyncSession,
        query_text: str,
        platform: Optional[str] = None,
        limit: int = 10,
        min_similarity: float = 0.0,
    ) -> List[Tuple[GeneratedPost, float]]:
        """Search for similar generated posts."""
        query_embedding = self.generate_embedding(query_text)

        platform_filter = "AND platform = :platform" if platform else ""

        query = text(f"""
            SELECT id, content, platform, status, engagement_rate,
                   1 - (embedding <=> :query_embedding) AS similarity
            FROM generated_posts
            WHERE embedding IS NOT NULL
              AND 1 - (embedding <=> :query_embedding) >= :min_similarity
              {platform_filter}
            ORDER BY embedding <=> :query_embedding
            LIMIT :limit
        """)

        params = {
            "query_embedding": query_embedding,
            "min_similarity": min_similarity,
            "limit": limit,
        }
        if platform:
            params["platform"] = platform

        result = await db.execute(query, params)
        rows = result.fetchall()

        posts_with_similarity = []
        for row in rows:
            post_result = await db.execute(
                select(GeneratedPost).filter(GeneratedPost.id == row.id)
            )
            post = post_result.scalar_one_or_none()
            if post:
                posts_with_similarity.append((post, row.similarity))

        logger.info(f"Found {len(posts_with_similarity)} similar posts")
        return posts_with_similarity

    async def search_similar_video_scenes(
        self,
        db: AsyncSession,
        query_text: str,
        video_id: Optional[str] = None,
        limit: int = 10,
        min_similarity: float = 0.0,
    ) -> List[Tuple[VideoScene, float]]:
        """Search for similar video scenes."""
        query_embedding = self.generate_embedding(query_text)

        video_filter = "AND video_id = :video_id" if video_id else ""

        query = text(f"""
            SELECT id, video_id, start_time, end_time, description, scene_type,
                   1 - (embedding <=> :query_embedding) AS similarity
            FROM video_scenes
            WHERE embedding IS NOT NULL
              AND 1 - (embedding <=> :query_embedding) >= :min_similarity
              {video_filter}
            ORDER BY embedding <=> :query_embedding
            LIMIT :limit
        """)

        params = {
            "query_embedding": query_embedding,
            "min_similarity": min_similarity,
            "limit": limit,
        }
        if video_id:
            params["video_id"] = video_id

        result = await db.execute(query, params)
        rows = result.fetchall()

        scenes_with_similarity = []
        for row in rows:
            scene_result = await db.execute(
                select(VideoScene).filter(VideoScene.id == row.id)
            )
            scene = scene_result.scalar_one_or_none()
            if scene:
                scenes_with_similarity.append((scene, row.similarity))

        logger.info(f"Found {len(scenes_with_similarity)} similar video scenes")
        return scenes_with_similarity

    async def find_similar_by_embedding(
        self,
        db: AsyncSession,
        embedding: List[float],
        model_class,
        limit: int = 10,
        min_similarity: float = 0.0,
    ) -> List[Tuple[any, float]]:
        """Generic similarity search by embedding vector."""
        table_name = model_class.__tablename__

        query = text(f"""
            SELECT id, 1 - (embedding <=> :query_embedding) AS similarity
            FROM {table_name}
            WHERE embedding IS NOT NULL
              AND 1 - (embedding <=> :query_embedding) >= :min_similarity
            ORDER BY embedding <=> :query_embedding
            LIMIT :limit
        """)

        result = await db.execute(
            query,
            {
                "query_embedding": embedding,
                "min_similarity": min_similarity,
                "limit": limit,
            },
        )
        rows = result.fetchall()

        objects_with_similarity = []
        for row in rows:
            obj_result = await db.execute(
                select(model_class).filter(model_class.id == row.id)
            )
            obj = obj_result.scalar_one_or_none()
            if obj:
                objects_with_similarity.append((obj, row.similarity))

        return objects_with_similarity


# ---------------------------------------------------------------------------
# Global instance
# ---------------------------------------------------------------------------
vector_service = VectorService()


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------
def generate_embedding(text: str) -> List[float]:
    """Generate embedding for a single text."""
    return vector_service.generate_embedding(text)


def generate_batch_embeddings(
    texts: List[str], batch_size: int = 32
) -> List[List[float]]:
    """Generate embeddings for multiple texts."""
    return vector_service.generate_batch_embeddings(texts, batch_size)


async def search_similar_articles(
    db: AsyncSession,
    query_text: str,
    limit: int = 10,
    min_similarity: float = 0.0,
) -> List[Tuple[Article, float]]:
    """Search for similar articles."""
    return await vector_service.search_similar_articles(
        db, query_text, limit, min_similarity
    )


async def search_similar_posts(
    db: AsyncSession,
    query_text: str,
    platform: Optional[str] = None,
    limit: int = 10,
    min_similarity: float = 0.0,
) -> List[Tuple[GeneratedPost, float]]:
    """Search for similar posts."""
    return await vector_service.search_similar_posts(
        db, query_text, platform, limit, min_similarity
    )


async def search_similar_video_scenes(
    db: AsyncSession,
    query_text: str,
    video_id: Optional[str] = None,
    limit: int = 10,
    min_similarity: float = 0.0,
) -> List[Tuple[VideoScene, float]]:
    """Search for similar video scenes."""
    return await vector_service.search_similar_video_scenes(
        db, query_text, video_id, limit, min_similarity
    )
