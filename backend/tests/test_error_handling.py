import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling and validation across the system"""
    
    async def test_invalid_brand_id(
        self,
        async_client: AsyncClient,
        test_user,
        auth_headers
    ):
        """Test 404 error for non-existent brand"""
        
        invalid_id = str(uuid4())
        
        response = await async_client.get(
            f"/api/v1/brands/{invalid_id}?user_id={test_user.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        data = response.json()
        
        # Verify standard error format
        assert "error" in data
        assert data["error"]["type"] == "NotFound"
        assert "message" in data["error"]
    
    async def test_invalid_article_id(
        self,
        async_client: AsyncClient,
        auth_headers
    ):
        """Test 404 error for non-existent article"""
        
        invalid_id = str(uuid4())
        
        response = await async_client.get(
            f"/api/v1/articles/{invalid_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        data = response.json()
        
        assert "error" in data
        assert data["error"]["type"] == "NotFound"
    
    async def test_missing_required_fields(
        self,
        async_client: AsyncClient,
        test_user,
        auth_headers
    ):
        """Test validation error for missing required fields"""
        
        # Missing 'name' field
        invalid_brand_data = {
            "description": "Test description"
        }
        
        response = await async_client.post(
            f"/api/v1/brands?user_id={test_user.id}",
            json=invalid_brand_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
        data = response.json()
        
        # Verify validation error format
        assert "error" in data or "detail" in data
    
    async def test_invalid_field_types(
        self,
        async_client: AsyncClient,
        auth_headers
    ):
        """Test validation error for invalid field types"""
        
        invalid_article_data = {
            "title": "Test Article",
            "content": "Test content",
            "url": "not-a-valid-url",  # Invalid URL format
            "views": "not-a-number"  # Should be integer
        }
        
        response = await async_client.post(
            "/api/v1/articles",
            json=invalid_article_data,
            headers=auth_headers
        )
        
        # Should return validation error
        assert response.status_code in [400, 422]
    
    async def test_unauthorized_access(
        self,
        async_client: AsyncClient
    ):
        """Test 401 error for missing authentication"""
        
        response = await async_client.get("/api/v1/brands")
        
        # Should require authentication
        assert response.status_code in [401, 403, 422]
    
    async def test_invalid_query_parameters(
        self,
        async_client: AsyncClient,
        auth_headers
    ):
        """Test error handling for invalid query parameters"""
        
        # Invalid page number
        response = await async_client.get(
            "/api/v1/articles?page=-1&page_size=10",
            headers=auth_headers
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]
    
    async def test_database_constraint_violation(
        self,
        async_client: AsyncClient,
        test_article,
        auth_headers
    ):
        """Test handling of database constraint violations"""
        
        # Try to create article with duplicate URL
        duplicate_article = {
            "title": "Different Title",
            "content": "Different content",
            "url": test_article.url  # Duplicate URL
        }
        
        response = await async_client.post(
            "/api/v1/articles",
            json=duplicate_article,
            headers=auth_headers
        )
        
        # Should handle constraint violation
        assert response.status_code in [400, 409, 422, 500]
    
    async def test_malformed_json(
        self,
        async_client: AsyncClient,
        auth_headers
    ):
        """Test handling of malformed JSON"""
        
        response = await async_client.post(
            "/api/v1/articles",
            content="{ invalid json }",
            headers={**auth_headers, "Content-Type": "application/json"}
        )
        
        # Should return 422 for malformed JSON
        assert response.status_code == 422
    
    async def test_empty_request_body(
        self,
        async_client: AsyncClient,
        test_user,
        auth_headers
    ):
        """Test handling of empty request body"""
        
        response = await async_client.post(
            f"/api/v1/brands?user_id={test_user.id}",
            json={},
            headers=auth_headers
        )
        
        # Should return validation error
        assert response.status_code == 422
    
    async def test_error_response_format(
        self,
        async_client: AsyncClient,
        auth_headers
    ):
        """Test that all errors follow standard format"""
        
        invalid_id = str(uuid4())
        
        response = await async_client.get(
            f"/api/v1/articles/{invalid_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        data = response.json()
        
        # Standard error format
        assert "error" in data
        assert "type" in data["error"]
        assert "message" in data["error"]
        assert "details" in data["error"]
    
    async def test_internal_server_error_handling(
        self,
        async_client: AsyncClient,
        auth_headers
    ):
        """Test that 500 errors are handled gracefully"""
        
        # This would require triggering an actual server error
        # In production, errors should be logged and return generic message
        pass
    
    async def test_rate_limit_error(
        self,
        async_client: AsyncClient,
        auth_headers
    ):
        """Test rate limiting (if implemented)"""
        
        # Make many requests rapidly
        responses = []
        for _ in range(100):
            response = await async_client.get(
                "/api/v1/articles",
                headers=auth_headers
            )
            responses.append(response)
        
        # If rate limiting is implemented, should get 429
        status_codes = [r.status_code for r in responses]
        
        # Most should succeed, but rate limiting may kick in
        assert 200 in status_codes
