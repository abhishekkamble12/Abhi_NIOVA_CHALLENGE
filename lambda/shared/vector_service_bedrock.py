"""
Vector Service using Amazon Bedrock
Updated to use Bedrock instead of SentenceTransformers
"""
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import os

# Import Bedrock service
from shared.bedrock_service import get_bedrock_service

# Import models
from app.models import Article, GeneratedPost, VideoScene


class VectorService:
    """
    Service for generating and searching vector embeddings using Bedrock
    """
    
    def __init__(self, cache_client=None):
        self.bedrock = get_bedrock_service(cache_client)
        self.dimension = 1536  # Bedrock Titan embeddings dimension
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding using Bedrock Titan
        
        Args:
            text: Input text
            
        Returns:
            1536-dimensional embedding vector
        """
        return self.bedrock.generate_embedding(text)
    
    def generate_batch_embeddings(
        self,
        texts: List[str],
        batch_size: int = 25
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of input texts
            batch_size: Batch size (not used by Bedrock)
            
        Returns:
            List of embedding vectors
        """
        return self.bedrock.generate_batch_embeddings(texts, batch_size)
    
    async def search_similar_articles(
        self,
        db: AsyncSession,
        query_text: str,
        limit: int = 10,
        min_similarity: float = 0.0
    ) -> List[Tuple[Article, float]]:
        """
        Search for similar articles using semantic search
        
        Args:
            db: Database session
            query_text: Search query
            limit: Maximum results
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of (Article, similarity_score) tuples
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(query_text)
        
        # Use cosine similarity (1 - cosine_distance)
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
                "limit": limit
            }
        )
        
        rows = result.fetchall()
        
        # Fetch full Article objects
        articles_with_similarity = []
        for row in rows:
            article_result = await db.execute(
                select(Article).filter(Article.id == row.id)
            )
            article = article_result.scalar_one_or_none()
            if article:
                articles_with_similarity.append((article, row.similarity))
        
        return articles_with_similarity
    
    async def search_similar_posts(
        self,
        db: AsyncSession,
        query_text: str,
        platform: Optional[str] = None,
        limit: int = 10,
        min_similarity: float = 0.0
    ) -> List[Tuple[GeneratedPost, float]]:
        """
        Search for similar generated posts
        """
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
            "limit": limit
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
        
        return posts_with_similarity
    
    async def search_similar_video_scenes(
        self,
        db: AsyncSession,
        query_text: str,
        video_id: Optional[str] = None,
        limit: int = 10,
        min_similarity: float = 0.0
    ) -> List[Tuple[VideoScene, float]]:
        """
        Search for similar video scenes
        """
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
            "limit": limit
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
        
        return scenes_with_similarity


# Global instance
vector_service = VectorService()


# Convenience functions
def generate_embedding(text: str) -> List[float]:
    """Generate embedding using Bedrock"""
    return vector_service.generate_embedding(text)


def generate_batch_embeddings(texts: List[str], batch_size: int = 25) -> List[List[float]]:
    """Generate batch embeddings using Bedrock"""
    return vector_service.generate_batch_embeddings(texts, batch_size)


async def search_similar_articles(
    db: AsyncSession,
    query_text: str,
    limit: int = 10,
    min_similarity: float = 0.0
) -> List[Tuple[Article, float]]:
    """Search for similar articles"""
    return await vector_service.search_similar_articles(db, query_text, limit, min_similarity)


async def search_similar_posts(
    db: AsyncSession,
    query_text: str,
    platform: Optional[str] = None,
    limit: int = 10,
    min_similarity: float = 0.0
) -> List[Tuple[GeneratedPost, float]]:
    """Search for similar posts"""
    return await vector_service.search_similar_posts(db, query_text, platform, limit, min_similarity)


async def search_similar_video_scenes(
    db: AsyncSession,
    query_text: str,
    video_id: Optional[str] = None,
    limit: int = 10,
    min_similarity: float = 0.0
) -> List[Tuple[VideoScene, float]]:
    """Search for similar video scenes"""
    return await vector_service.search_similar_video_scenes(db, query_text, video_id, limit, min_similarity)
