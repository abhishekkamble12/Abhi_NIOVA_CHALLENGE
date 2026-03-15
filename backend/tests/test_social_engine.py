import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Brand, GeneratedPost
from app.schemas.brand import BrandCreate


@pytest.mark.integration
class TestSocialMediaEngine:
    """Test social media content generation and management"""
    
    async def test_create_brand_flow(
        self,
        async_client: AsyncClient,
        test_user,
        auth_headers
    ):
        """Test complete brand creation flow"""
        
        brand_data = {
            "name": "TechStartup Inc",
            "description": "Innovative tech solutions for modern businesses",
            "industry": "Technology",
            "tone": "professional",
            "brand_voice": "Clear, concise, and authoritative"
        }
        
        response = await async_client.post(
            f"/api/v1/brands?user_id={test_user.id}",
            json=brand_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert data["name"] == brand_data["name"]
        assert data["description"] == brand_data["description"]
        assert data["industry"] == brand_data["industry"]
        assert "id" in data
        assert "created_at" in data
    
    async def test_brand_embedding_generated(
        self,
        db_session: AsyncSession,
        test_brand
    ):
        """Test that brand embedding is generated and stored"""
        
        # Refresh to get latest data
        await db_session.refresh(test_brand)
        
        # Verify embedding exists
        assert test_brand.embedding is not None
        assert len(test_brand.embedding) == 1024
    
    async def test_generate_social_post(
        self,
        async_client: AsyncClient,
        test_user,
        test_brand,
        auth_headers
    ):
        """Test social media post generation"""
        
        post_data = {
            "brand_id": str(test_brand.id),
            "platform": "linkedin",
            "content": "Excited to announce our new AI-powered platform!",
            "hashtags": "#AI #Innovation #Tech"
        }
        
        response = await async_client.post(
            f"/api/v1/posts?user_id={test_user.id}",
            json=post_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["platform"] == "linkedin"
        assert data["content"] == post_data["content"]
        assert "id" in data
    
    async def test_retrieve_brand_posts(
        self,
        async_client: AsyncClient,
        test_brand,
        auth_headers
    ):
        """Test retrieving posts for a brand"""
        
        response = await async_client.get(
            f"/api/v1/brands/{test_brand.id}/posts",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "posts" in data
        assert isinstance(data["posts"], list)
    
    async def test_post_embedding_storage(
        self,
        db_session: AsyncSession,
        test_user,
        test_brand
    ):
        """Test that generated post embeddings are stored"""
        
        from app.models import GeneratedPost, PlatformType, PostStatus
        
        post = GeneratedPost(
            user_id=test_user.id,
            brand_id=test_brand.id,
            platform=PlatformType.LINKEDIN,
            status=PostStatus.PUBLISHED,
            content="Test post content",
            embedding=[0.5] * 1024
        )
        
        db_session.add(post)
        await db_session.commit()
        await db_session.refresh(post)
        
        # Verify embedding stored
        assert post.embedding is not None
        assert len(post.embedding) == 1024
    
    async def test_update_brand(
        self,
        async_client: AsyncClient,
        test_user,
        test_brand,
        auth_headers
    ):
        """Test brand update flow"""
        
        update_data = {
            "description": "Updated brand description",
            "tone": "casual"
        }
        
        response = await async_client.put(
            f"/api/v1/brands/{test_brand.id}?user_id={test_user.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["description"] == update_data["description"]
        assert data["tone"] == update_data["tone"]
    
    async def test_list_user_brands(
        self,
        async_client: AsyncClient,
        test_user,
        test_brand,
        auth_headers
    ):
        """Test listing all brands for a user"""
        
        response = await async_client.get(
            f"/api/v1/brands?user_id={test_user.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "brands" in data
        assert data["total"] >= 1
        assert len(data["brands"]) >= 1
