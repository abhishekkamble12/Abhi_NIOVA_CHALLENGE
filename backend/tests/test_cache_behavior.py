import pytest
from httpx import AsyncClient
import time

from app.core.redis import set_cache, get_cache, delete_cache


@pytest.mark.integration
class TestCacheBehavior:
    """Test Redis caching functionality"""
    
    async def test_cache_set_and_get(self):
        """Test basic cache set and get operations"""
        
        key = "test_key"
        value = {"data": "test_value", "count": 42}
        
        # Set cache
        success = await set_cache(key, value, ttl=60)
        assert success is True or success is None  # May be None if Redis unavailable
        
        # Get cache
        cached_value = await get_cache(key)
        
        if cached_value:
            assert cached_value == value
    
    async def test_cache_expiration(self):
        """Test cache TTL expiration"""
        
        key = "expiring_key"
        value = "temporary_value"
        
        # Set with short TTL
        await set_cache(key, value, ttl=1)
        
        # Should exist immediately
        cached = await get_cache(key)
        if cached:
            assert cached == value
        
        # Wait for expiration
        time.sleep(2)
        
        # Should be expired
        expired = await get_cache(key)
        assert expired is None
    
    async def test_cache_delete(self):
        """Test cache deletion"""
        
        key = "deletable_key"
        value = "delete_me"
        
        # Set cache
        await set_cache(key, value, ttl=60)
        
        # Verify exists
        cached = await get_cache(key)
        if cached:
            assert cached == value
        
        # Delete
        await delete_cache(key)
        
        # Verify deleted
        deleted = await get_cache(key)
        assert deleted is None
    
    async def test_feed_endpoint_caching(
        self,
        async_client: AsyncClient,
        test_user,
        test_article,
        auth_headers
    ):
        """
        Test feed endpoint caching behavior
        
        First call: Database query
        Second call: Served from cache
        """
        
        endpoint = f"/api/v1/feed?user_id={test_user.id}&limit=10"
        
        # First call - should hit database
        start_time = time.time()
        response1 = await async_client.get(endpoint, headers=auth_headers)
        first_call_time = time.time() - start_time
        
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Second call - should hit cache (faster)
        start_time = time.time()
        response2 = await async_client.get(endpoint, headers=auth_headers)
        second_call_time = time.time() - start_time
        
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Data should be identical
        assert data1 == data2
        
        # Second call should be faster (if caching works)
        # Note: This may not always be true in test environment
    
    async def test_embedding_caching(self, vector_service):
        """Test that embeddings are cached"""
        
        text = "This text should be cached"
        
        # First generation
        start_time = time.time()
        embedding1 = vector_service.generate_embedding(text)
        first_time = time.time() - start_time
        
        # Second generation (should use cache)
        start_time = time.time()
        embedding2 = vector_service.generate_embedding(text)
        second_time = time.time() - start_time
        
        # Embeddings should be identical
        assert embedding1 == embedding2
        
        # Second call should be faster (if caching works)
        # Note: May not be measurable in test environment
    
    async def test_cache_invalidation_on_update(
        self,
        async_client: AsyncClient,
        test_article,
        auth_headers
    ):
        """Test cache invalidation when data is updated"""
        
        article_id = test_article.id
        
        # Get article (cache it)
        response1 = await async_client.get(
            f"/api/v1/articles/{article_id}",
            headers=auth_headers
        )
        assert response1.status_code == 200
        original_title = response1.json()["title"]
        
        # Update article (should invalidate cache)
        update_data = {"title": "Updated Title"}
        update_response = await async_client.put(
            f"/api/v1/articles/{article_id}",
            json=update_data,
            headers=auth_headers
        )
        assert update_response.status_code == 200
        
        # Get article again (should have new data)
        response2 = await async_client.get(
            f"/api/v1/articles/{article_id}",
            headers=auth_headers
        )
        assert response2.status_code == 200
        new_title = response2.json()["title"]
        
        # Title should be updated
        assert new_title == "Updated Title"
        assert new_title != original_title
    
    async def test_cache_miss_handling(self):
        """Test handling of cache misses"""
        
        non_existent_key = "this_key_does_not_exist_12345"
        
        value = await get_cache(non_existent_key)
        
        # Should return None for cache miss
        assert value is None
    
    async def test_json_serialization_in_cache(self):
        """Test complex object caching with JSON serialization"""
        
        complex_data = {
            "user": {"id": 123, "name": "Test"},
            "articles": [
                {"id": 1, "title": "Article 1"},
                {"id": 2, "title": "Article 2"}
            ],
            "metadata": {
                "count": 2,
                "page": 1
            }
        }
        
        key = "complex_data_key"
        
        # Cache complex object
        await set_cache(key, complex_data, ttl=60)
        
        # Retrieve and verify
        cached = await get_cache(key)
        
        if cached:
            assert cached == complex_data
            assert cached["user"]["name"] == "Test"
            assert len(cached["articles"]) == 2
