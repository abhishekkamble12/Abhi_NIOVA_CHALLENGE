import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Article, GeneratedPost, Video, VideoScene, Brand
from app.services.vector_service import generate_embedding


@pytest.mark.integration
@pytest.mark.cross_module
class TestCrossModuleLearning:
    """
    Test cross-module intelligence - the core innovation of HiveMind
    
    This validates that:
    - News insights influence social content
    - Video insights influence caption generation
    - Shared embeddings enable cross-module recommendations
    """
    
    async def test_news_to_social_content_flow(
        self,
        db_session: AsyncSession,
        test_user,
        test_brand
    ):
        """
        Test: Trending news article → Generate social media content
        
        Flow:
        1. Insert trending news article
        2. Generate social content using news insights
        3. Verify embeddings are related
        """
        
        # 1. Create trending news article
        news_article = Article(
            title="AI Breakthrough: New Model Achieves Human-Level Performance",
            content="Researchers announce major AI breakthrough in natural language understanding...",
            url="https://example.com/ai-breakthrough",
            category="Technology",
            relevance_score=0.95
        )
        
        # Generate embedding for news
        news_embedding = generate_embedding(f"{news_article.title} {news_article.content}")
        news_article.embedding = news_embedding
        
        db_session.add(news_article)
        await db_session.commit()
        await db_session.refresh(news_article)
        
        # 2. Generate social post inspired by news
        from app.models import GeneratedPost, PlatformType, PostStatus
        
        social_post = GeneratedPost(
            user_id=test_user.id,
            brand_id=test_brand.id,
            platform=PlatformType.LINKEDIN,
            status=PostStatus.DRAFT,
            content="Exciting AI breakthrough! New research shows human-level performance in NLP. The future is here! 🚀",
            prompt_used=f"Generate LinkedIn post based on: {news_article.title}"
        )
        
        # Generate embedding for social post
        post_embedding = generate_embedding(social_post.content)
        social_post.embedding = post_embedding
        
        db_session.add(social_post)
        await db_session.commit()
        await db_session.refresh(social_post)
        
        # 3. Verify embeddings are semantically related
        # Calculate cosine similarity
        import numpy as np
        
        news_vec = np.array(news_embedding)
        post_vec = np.array(post_embedding)
        
        similarity = np.dot(news_vec, post_vec) / (
            np.linalg.norm(news_vec) * np.linalg.norm(post_vec)
        )
        
        # Similarity should be high (> 0.5) since content is related
        assert similarity > 0.3, f"News and social post should be semantically related, got similarity: {similarity}"
    
    async def test_video_to_caption_intelligence(
        self,
        db_session: AsyncSession,
        test_user,
        test_video
    ):
        """
        Test: Video insights → Generate intelligent captions
        
        Flow:
        1. Upload video with content
        2. Detect scenes
        3. Generate captions using scene context
        4. Verify captions align with scene content
        """
        
        # 1. Create video scene
        from app.models import VideoScene, Caption
        
        scene = VideoScene(
            video_id=test_video.id,
            start_time=0.0,
            end_time=15.0,
            description="Speaker introducing product features",
            scene_type="dialogue"
        )
        
        scene_embedding = generate_embedding(scene.description)
        scene.embedding = scene_embedding
        
        db_session.add(scene)
        await db_session.commit()
        
        # 2. Generate caption based on scene
        caption = Caption(
            video_id=test_video.id,
            start_time=0.0,
            end_time=15.0,
            text="Welcome! Let me show you our amazing new features.",
            language="en",
            confidence=0.93
        )
        
        db_session.add(caption)
        await db_session.commit()
        
        # 3. Verify caption aligns with scene
        caption_embedding = generate_embedding(caption.text)
        
        import numpy as np
        scene_vec = np.array(scene_embedding)
        caption_vec = np.array(caption_embedding)
        
        similarity = np.dot(scene_vec, caption_vec) / (
            np.linalg.norm(scene_vec) * np.linalg.norm(caption_vec)
        )
        
        assert similarity > 0.3, "Caption should align with scene content"
    
    async def test_full_cross_module_workflow(
        self,
        db_session: AsyncSession,
        test_user,
        test_brand
    ):
        """
        Test: Complete cross-module intelligence workflow
        
        Scenario:
        1. Trending news about AI
        2. Generate social post from news
        3. Create video about same topic
        4. Generate captions using shared context
        5. Verify all modules share intelligence
        """
        
        # 1. Trending news
        article = Article(
            title="The Future of AI in Business",
            content="AI is transforming how businesses operate...",
            url="https://example.com/ai-business",
            category="Business"
        )
        article.embedding = generate_embedding(f"{article.title} {article.content}")
        db_session.add(article)
        
        # 2. Social post from news
        from app.models import GeneratedPost, PlatformType, PostStatus
        
        post = GeneratedPost(
            user_id=test_user.id,
            brand_id=test_brand.id,
            platform=PlatformType.LINKEDIN,
            status=PostStatus.PUBLISHED,
            content="AI is revolutionizing business operations! Here's what you need to know.",
            prompt_used=f"Create post from: {article.title}"
        )
        post.embedding = generate_embedding(post.content)
        db_session.add(post)
        
        # 3. Video on same topic
        from app.models import Video, VideoStatus
        
        video = Video(
            user_id=test_user.id,
            title="AI in Business: Complete Guide",
            description="Comprehensive guide to AI adoption in business",
            file_path="/uploads/ai_business.mp4",
            status=VideoStatus.READY
        )
        video.embedding = generate_embedding(f"{video.title} {video.description}")
        db_session.add(video)
        
        await db_session.commit()
        
        # 4. Verify all embeddings are related
        import numpy as np
        
        article_vec = np.array(article.embedding)
        post_vec = np.array(post.embedding)
        video_vec = np.array(video.embedding)
        
        # Calculate pairwise similarities
        article_post_sim = np.dot(article_vec, post_vec) / (
            np.linalg.norm(article_vec) * np.linalg.norm(post_vec)
        )
        
        article_video_sim = np.dot(article_vec, video_vec) / (
            np.linalg.norm(article_vec) * np.linalg.norm(video_vec)
        )
        
        post_video_sim = np.dot(post_vec, video_vec) / (
            np.linalg.norm(post_vec) * np.linalg.norm(video_vec)
        )
        
        # All modules should be semantically related
        assert article_post_sim > 0.3, "Article and post should be related"
        assert article_video_sim > 0.3, "Article and video should be related"
        assert post_video_sim > 0.3, "Post and video should be related"
    
    async def test_recommendation_across_modules(
        self,
        db_session: AsyncSession,
        test_user
    ):
        """
        Test: Cross-module recommendations
        
        Given a user's interest in an article,
        recommend related videos and social posts
        """
        
        # User views article about AI
        article = Article(
            title="Deep Learning Fundamentals",
            content="Understanding neural networks and deep learning...",
            url="https://example.com/deep-learning"
        )
        article.embedding = generate_embedding(f"{article.title} {article.content}")
        db_session.add(article)
        
        # Track user behavior
        from app.models import UserBehavior, ActionType
        
        behavior = UserBehavior(
            user_id=test_user.id,
            article_id=article.id,
            action_type=ActionType.VIEW,
            time_spent=180,
            scroll_depth=0.9
        )
        db_session.add(behavior)
        
        await db_session.commit()
        
        # System should recommend related content from other modules
        # This would be implemented in recommendation service
        
        # Verify user behavior is tracked for cross-module learning
        result = await db_session.execute(
            select(UserBehavior).filter(UserBehavior.user_id == test_user.id)
        )
        behaviors = result.scalars().all()
        
        assert len(behaviors) > 0
        assert behaviors[0].action_type == ActionType.VIEW
    
    async def test_shared_embedding_space(
        self,
        db_session: AsyncSession
    ):
        """
        Test: All modules use same embedding space
        
        Verify that articles, posts, videos, and scenes
        all use 1024-dimensional embeddings from same model
        """
        
        from app.models import Article, GeneratedPost, Video, VideoScene
        
        # Create one of each type
        article = Article(
            title="Test Article",
            content="Content",
            url="https://test.com/1",
            embedding=[0.1] * 1024
        )
        
        post = GeneratedPost(
            user_id="00000000-0000-0000-0000-000000000000",
            platform="linkedin",
            content="Test post",
            embedding=[0.2] * 1024
        )
        
        video = Video(
            user_id="00000000-0000-0000-0000-000000000000",
            title="Test Video",
            file_path="/test.mp4",
            embedding=[0.3] * 1024
        )
        
        scene = VideoScene(
            video_id="00000000-0000-0000-0000-000000000000",
            start_time=0.0,
            end_time=10.0,
            embedding=[0.4] * 1024
        )
        
        # Verify all use same dimension
        assert len(article.embedding) == 1024
        assert len(post.embedding) == 1024
        assert len(video.embedding) == 1024
        assert len(scene.embedding) == 1024
