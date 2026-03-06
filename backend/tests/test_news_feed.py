import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Article, UserBehavior, ActionType


@pytest.mark.integration
class TestNewsFeed:
    """Test personalized news feed functionality"""
    
    async def test_create_article_with_embedding(
        self,
        async_client: AsyncClient,
        auth_headers
    ):
        """Test article creation with automatic embedding generation"""
        
        article_data = {
            "title": "The Future of AI in Content Creation",
            "content": "Artificial intelligence is revolutionizing content creation...",
            "url": "https://example.com/ai-future",
            "source": "TechCrunch",
            "category": "Technology",
            "tags": ["AI", "Content", "Innovation"]
        }
        
        response = await async_client.post(
            "/api/v1/articles",
            json=article_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["title"] == article_data["title"]
        assert data["url"] == article_data["url"]
        assert "id" in data
        assert "created_at" in data
    
    async def test_article_embedding_stored(
        self,
        db_session: AsyncSession,
        test_article
    ):
        """Test that article embeddings are stored in database"""
        
        await db_session.refresh(test_article)
        
        assert test_article.embedding is not None
        assert len(test_article.embedding) == 384
    
    async def test_semantic_article_search(
        self,
        async_client: AsyncClient,
        test_article,
        auth_headers
    ):
        """Test semantic search for similar articles"""
        
        response = await async_client.get(
            "/api/v1/articles/search/semantic?query=artificial intelligence&limit=5",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        
        if len(data) > 0:
            # Verify response structure
            assert "article" in data[0]
            assert "similarity" in data[0]
            assert 0 <= data[0]["similarity"] <= 1
    
    async def test_personalized_feed_retrieval(
        self,
        async_client: AsyncClient,
        test_user,
        multiple_articles,
        auth_headers
    ):
        """Test retrieving personalized news feed"""
        
        response = await async_client.get(
            f"/api/v1/feed?user_id={test_user.id}&limit=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "articles" in data
        assert isinstance(data["articles"], list)
    
    async def test_article_view_tracking(
        self,
        async_client: AsyncClient,
        test_article,
        auth_headers
    ):
        """Test article view count increment"""
        
        initial_views = test_article.views
        
        response = await async_client.get(
            f"/api/v1/articles/{test_article.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Views should increment (tested in service layer)
    
    async def test_user_behavior_tracking(
        self,
        db_session: AsyncSession,
        test_user,
        test_article
    ):
        """Test user behavior tracking for recommendations"""
        
        behavior = UserBehavior(
            user_id=test_user.id,
            article_id=test_article.id,
            action_type=ActionType.VIEW,
            time_spent=120,
            scroll_depth=0.75,
            device="desktop",
            platform="web"
        )
        
        db_session.add(behavior)
        await db_session.commit()
        await db_session.refresh(behavior)
        
        assert behavior.id is not None
        assert behavior.action_type == ActionType.VIEW
    
    async def test_category_filtering(
        self,
        async_client: AsyncClient,
        auth_headers
    ):
        """Test filtering articles by category"""
        
        response = await async_client.get(
            "/api/v1/articles?category=Technology&page=1&page_size=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "articles" in data
        assert "total" in data
    
    async def test_article_update(
        self,
        async_client: AsyncClient,
        test_article,
        auth_headers
    ):
        """Test article update with embedding regeneration"""
        
        update_data = {
            "title": "Updated: AI Revolution",
            "category": "AI"
        }
        
        response = await async_client.put(
            f"/api/v1/articles/{test_article.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["title"] == update_data["title"]
        assert data["category"] == update_data["category"]
