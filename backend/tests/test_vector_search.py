import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.vector_service import generate_embedding, generate_batch_embeddings
from app.models import Article, GeneratedPost, VideoScene


@pytest.mark.integration
@pytest.mark.vector
class TestVectorSearch:
    """Test vector embedding and semantic search functionality"""
    
    async def test_embedding_generation(self, vector_service):
        """Test single embedding generation"""
        
        text = "Artificial intelligence is transforming content creation"
        embedding = vector_service.generate_embedding(text)
        
        assert embedding is not None
        assert len(embedding) == 1024
        assert all(isinstance(x, float) for x in embedding)
    
    async def test_batch_embedding_generation(self, vector_service):
        """Test efficient batch embedding generation"""
        
        texts = [
            "First article about AI",
            "Second article about machine learning",
            "Third article about deep learning"
        ]
        
        embeddings = vector_service.generate_batch_embeddings(texts, batch_size=32)
        
        assert len(embeddings) == 3
        assert all(len(emb) == 1024 for emb in embeddings)
    
    async def test_article_semantic_search(
        self,
        db_session: AsyncSession,
        multiple_articles
    ):
        """Test semantic search across articles"""
        
        from app.services.vector_service import search_similar_articles
        
        query = "machine learning fundamentals"
        
        results = await search_similar_articles(
            db=db_session,
            query_text=query,
            limit=5,
            min_similarity=0.0
        )
        
        assert len(results) <= 5
        
        # Verify results are sorted by similarity
        if len(results) > 1:
            similarities = [sim for _, sim in results]
            assert similarities == sorted(similarities, reverse=True)
    
    async def test_post_semantic_search(
        self,
        db_session: AsyncSession,
        test_user,
        test_brand
    ):
        """Test semantic search for social posts"""
        
        from app.models import GeneratedPost, PlatformType, PostStatus
        from app.services.vector_service import search_similar_posts
        
        # Create posts with embeddings
        posts = [
            GeneratedPost(
                user_id=test_user.id,
                brand_id=test_brand.id,
                platform=PlatformType.LINKEDIN,
                status=PostStatus.PUBLISHED,
                content=f"Post about AI and technology {i}",
                embedding=generate_embedding(f"AI technology post {i}")
            )
            for i in range(3)
        ]
        
        db_session.add_all(posts)
        await db_session.commit()
        
        # Search for similar posts
        results = await search_similar_posts(
            db=db_session,
            query_text="artificial intelligence",
            limit=5
        )
        
        assert len(results) <= 5
    
    async def test_video_scene_semantic_search(
        self,
        db_session: AsyncSession,
        test_video
    ):
        """Test semantic search for video scenes"""
        
        from app.models import VideoScene
        from app.services.vector_service import search_similar_video_scenes
        
        # Create scenes with embeddings
        scenes = [
            VideoScene(
                video_id=test_video.id,
                start_time=i * 10.0,
                end_time=(i + 1) * 10.0,
                description=f"Scene showing product feature {i}",
                embedding=generate_embedding(f"product feature {i}")
            )
            for i in range(3)
        ]
        
        db_session.add_all(scenes)
        await db_session.commit()
        
        # Search for similar scenes
        results = await search_similar_video_scenes(
            db=db_session,
            query_text="product demonstration",
            limit=5
        )
        
        assert len(results) <= 5
    
    async def test_similarity_score_range(
        self,
        db_session: AsyncSession,
        test_article
    ):
        """Test that similarity scores are in valid range [0, 1]"""
        
        from app.services.vector_service import search_similar_articles
        
        results = await search_similar_articles(
            db=db_session,
            query_text="test query",
            limit=10,
            min_similarity=0.0
        )
        
        for article, similarity in results:
            assert 0.0 <= similarity <= 1.0, f"Similarity {similarity} out of range"
    
    async def test_min_similarity_filter(
        self,
        db_session: AsyncSession,
        multiple_articles
    ):
        """Test minimum similarity threshold filtering"""
        
        from app.services.vector_service import search_similar_articles
        
        # Search with high threshold
        results_high = await search_similar_articles(
            db=db_session,
            query_text="machine learning",
            limit=10,
            min_similarity=0.8
        )
        
        # Search with low threshold
        results_low = await search_similar_articles(
            db=db_session,
            query_text="machine learning",
            limit=10,
            min_similarity=0.3
        )
        
        # Low threshold should return more or equal results
        assert len(results_low) >= len(results_high)
    
    async def test_empty_query_handling(self, vector_service):
        """Test handling of empty or invalid queries"""
        
        empty_embedding = vector_service.generate_embedding("")
        
        # Should return zero vector or handle gracefully
        assert len(empty_embedding) == 1024
    
    async def test_cross_module_vector_search(
        self,
        db_session: AsyncSession,
        test_user,
        test_brand,
        test_video
    ):
        """Test finding related content across different modules"""
        
        # Create content in different modules with related embeddings
        topic = "artificial intelligence innovation"
        topic_embedding = generate_embedding(topic)
        
        # Article
        article = Article(
            title="AI Innovation Trends",
            content="Latest trends in AI...",
            url="https://example.com/ai-trends",
            embedding=topic_embedding
        )
        db_session.add(article)
        
        # Social post
        from app.models import GeneratedPost, PlatformType
        post = GeneratedPost(
            user_id=test_user.id,
            brand_id=test_brand.id,
            platform=PlatformType.LINKEDIN,
            content="Exploring AI innovation...",
            embedding=topic_embedding
        )
        db_session.add(post)
        
        # Video scene
        from app.models import VideoScene
        scene = VideoScene(
            video_id=test_video.id,
            start_time=0.0,
            end_time=30.0,
            description="Discussion about AI innovation",
            embedding=topic_embedding
        )
        db_session.add(scene)
        
        await db_session.commit()
        
        # Search should find related content across all modules
        from app.services.vector_service import (
            search_similar_articles,
            search_similar_posts,
            search_similar_video_scenes
        )
        
        article_results = await search_similar_articles(db_session, topic, limit=5)
        post_results = await search_similar_posts(db_session, topic, limit=5)
        scene_results = await search_similar_video_scenes(db_session, topic, limit=5)
        
        # All modules should return results
        assert len(article_results) > 0
        assert len(post_results) > 0
        assert len(scene_results) > 0
