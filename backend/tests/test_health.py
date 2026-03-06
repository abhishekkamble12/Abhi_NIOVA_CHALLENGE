import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestSystemHealth:
    """Test system health and connectivity"""
    
    async def test_health_endpoint(self, async_client: AsyncClient):
        """Test health check endpoint"""
        response = await async_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "database" in data
        assert "redis" in data
    
    async def test_root_endpoint(self, async_client: AsyncClient):
        """Test root endpoint"""
        response = await async_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "version" in data
        assert data["status"] == "✅ Running"
    
    async def test_api_docs_available(self, async_client: AsyncClient):
        """Test OpenAPI docs are accessible"""
        response = await async_client.get("/docs")
        
        assert response.status_code == 200
    
    async def test_database_connection(self, db_session):
        """Test database connection is working"""
        from sqlalchemy import text
        
        result = await db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1
