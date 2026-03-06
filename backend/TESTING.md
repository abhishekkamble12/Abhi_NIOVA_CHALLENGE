# Integration Testing Framework for HiveMind

## Overview

Comprehensive integration testing framework validating the full AI Media OS system including cross-module intelligence, vector embeddings, and semantic search.

## Test Structure

```
tests/
├── conftest.py                      # Test fixtures and configuration
├── test_health.py                   # System health tests
├── test_social_engine.py            # Social media module tests
├── test_news_feed.py                # News feed module tests
├── test_video_intelligence.py       # Video processing tests
├── test_cross_module_learning.py    # Cross-module intelligence tests ⭐
├── test_vector_search.py            # Vector embedding tests
├── test_cache_behavior.py           # Redis caching tests
└── test_error_handling.py           # Error handling tests
```

## Key Features

✅ **Isolated Test Database** - In-memory SQLite with transaction rollback  
✅ **Async Testing** - Full async/await support with pytest-asyncio  
✅ **Comprehensive Fixtures** - Reusable test data and clients  
✅ **Cross-Module Validation** - Tests shared intelligence across modules  
✅ **Vector Search Testing** - Validates semantic similarity  
✅ **Cache Behavior Testing** - Verifies Redis caching  
✅ **Error Handling** - Tests all error scenarios  

## Running Tests

### Run All Tests

```bash
cd backend
pytest
```

### Run Specific Test Module

```bash
pytest tests/test_cross_module_learning.py
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

### Run Integration Tests Only

```bash
pytest -m integration
```

### Run Cross-Module Tests Only

```bash
pytest -m cross_module
```

### Run Vector Tests Only

```bash
pytest -m vector
```

### Verbose Output

```bash
pytest -v
```

## Test Fixtures

### Database Fixtures

**`test_engine`** - Test database engine (session scope)
```python
async def test_example(test_engine):
    # Use test database engine
```

**`db_session`** - Database session with rollback (function scope)
```python
async def test_example(db_session):
    # Changes rolled back after test
```

### Application Fixtures

**`test_app`** - FastAPI app with overridden dependencies
```python
async def test_example(test_app):
    # Use test app instance
```

**`async_client`** - HTTP client for API testing
```python
async def test_example(async_client):
    response = await async_client.get("/api/v1/articles")
```

### Data Fixtures

**`test_user`** - Test user instance
```python
async def test_example(test_user):
    assert test_user.email == "test@example.com"
```

**`test_brand`** - Test brand instance
```python
async def test_example(test_brand):
    assert test_brand.name == "Test Brand"
```

**`test_article`** - Test article instance
```python
async def test_example(test_article):
    assert test_article.embedding is not None
```

**`test_video`** - Test video instance
```python
async def test_example(test_video):
    assert test_video.status == "ready"
```

**`auth_headers`** - Authentication headers
```python
async def test_example(async_client, auth_headers):
    response = await async_client.get("/api/v1/brands", headers=auth_headers)
```

### Service Fixtures

**`vector_service`** - Vector embedding service
```python
def test_example(vector_service):
    embedding = vector_service.generate_embedding("test")
```

**`redis_client_fixture`** - Redis client
```python
async def test_example(redis_client_fixture):
    # Use Redis client
```

## Test Categories

### 1. System Health Tests

**Purpose**: Validate system is running and connected

**Tests**:
- Health endpoint returns 200
- Database connection works
- Redis connection works
- API docs accessible

**Example**:
```python
async def test_health_endpoint(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### 2. Social Media Engine Tests

**Purpose**: Validate social media content generation

**Tests**:
- Create brand with embedding
- Generate social posts
- Store post embeddings
- Retrieve brand posts
- Update brand

**Example**:
```python
async def test_create_brand_flow(async_client, test_user, auth_headers):
    brand_data = {
        "name": "TechStartup Inc",
        "description": "Innovative tech solutions"
    }
    response = await async_client.post(
        f"/api/v1/brands?user_id={test_user.id}",
        json=brand_data,
        headers=auth_headers
    )
    assert response.status_code == 201
```

### 3. News Feed Tests

**Purpose**: Validate personalized news feed

**Tests**:
- Create article with embedding
- Semantic article search
- Personalized feed retrieval
- User behavior tracking
- Category filtering

**Example**:
```python
async def test_semantic_article_search(async_client, test_article, auth_headers):
    response = await async_client.get(
        "/api/v1/articles/search/semantic?query=AI&limit=5",
        headers=auth_headers
    )
    assert response.status_code == 200
```

### 4. Video Intelligence Tests

**Purpose**: Validate video processing

**Tests**:
- Video upload and metadata
- Scene detection
- Caption generation
- Video transcript
- Scene similarity search

**Example**:
```python
async def test_scene_detection(db_session, test_video):
    scene = VideoScene(
        video_id=test_video.id,
        start_time=0.0,
        end_time=10.0,
        description="Opening scene",
        embedding=[0.1] * 384
    )
    db_session.add(scene)
    await db_session.commit()
```

### 5. Cross-Module Learning Tests ⭐

**Purpose**: Validate shared intelligence across modules

**Tests**:
- News → Social content flow
- Video → Caption intelligence
- Full cross-module workflow
- Cross-module recommendations
- Shared embedding space

**Example**:
```python
async def test_news_to_social_content_flow(db_session, test_user, test_brand):
    # Create news article
    article = Article(
        title="AI Breakthrough",
        content="Major AI advancement...",
        embedding=generate_embedding("AI breakthrough")
    )
    db_session.add(article)
    
    # Generate social post from news
    post = GeneratedPost(
        user_id=test_user.id,
        brand_id=test_brand.id,
        content="Exciting AI breakthrough!",
        embedding=generate_embedding("AI breakthrough")
    )
    db_session.add(post)
    
    await db_session.commit()
    
    # Verify embeddings are related
    similarity = calculate_similarity(article.embedding, post.embedding)
    assert similarity > 0.3
```

### 6. Vector Search Tests

**Purpose**: Validate semantic search functionality

**Tests**:
- Embedding generation
- Batch embedding generation
- Article semantic search
- Post semantic search
- Scene semantic search
- Similarity score validation
- Cross-module vector search

**Example**:
```python
async def test_article_semantic_search(db_session, multiple_articles):
    results = await search_similar_articles(
        db=db_session,
        query_text="machine learning",
        limit=5
    )
    assert len(results) <= 5
    # Verify sorted by similarity
    similarities = [sim for _, sim in results]
    assert similarities == sorted(similarities, reverse=True)
```

### 7. Cache Behavior Tests

**Purpose**: Validate Redis caching

**Tests**:
- Cache set and get
- Cache expiration
- Cache deletion
- Feed endpoint caching
- Embedding caching
- Cache invalidation on update

**Example**:
```python
async def test_feed_endpoint_caching(async_client, test_user, auth_headers):
    endpoint = f"/api/v1/feed?user_id={test_user.id}"
    
    # First call - database
    response1 = await async_client.get(endpoint, headers=auth_headers)
    
    # Second call - cache
    response2 = await async_client.get(endpoint, headers=auth_headers)
    
    # Data should be identical
    assert response1.json() == response2.json()
```

### 8. Error Handling Tests

**Purpose**: Validate error responses

**Tests**:
- Invalid IDs (404)
- Missing required fields (422)
- Invalid field types (422)
- Unauthorized access (401)
- Database constraints (409)
- Malformed JSON (422)
- Standard error format

**Example**:
```python
async def test_invalid_brand_id(async_client, test_user, auth_headers):
    invalid_id = str(uuid4())
    response = await async_client.get(
        f"/api/v1/brands/{invalid_id}?user_id={test_user.id}",
        headers=auth_headers
    )
    assert response.status_code == 404
    assert "error" in response.json()
```

## Test Database

### Configuration

Tests use in-memory SQLite database:
```python
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
```

### Isolation

Each test runs in a transaction that is rolled back:
```python
@pytest.fixture
async def db_session(test_engine):
    async with async_session() as session:
        async with session.begin():
            yield session
            await session.rollback()  # Rollback after test
```

### Schema Creation

Tables are created once per test session:
```python
@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()
```

## Coverage

Generate coverage report:
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

Target coverage: **> 80%**

## CI/CD Integration

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=app
```

## Best Practices

1. **Isolation**: Each test is independent
2. **Fixtures**: Reuse test data via fixtures
3. **Async**: Use async/await for all async operations
4. **Assertions**: Clear, specific assertions
5. **Naming**: Descriptive test names
6. **Documentation**: Docstrings explain test purpose
7. **Markers**: Use pytest markers for categorization

## Troubleshooting

### Tests Fail to Import

```bash
# Ensure PYTHONPATH includes backend directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Database Errors

```bash
# Ensure test database is clean
pytest --create-db
```

### Async Errors

```bash
# Ensure pytest-asyncio is installed
pip install pytest-asyncio
```

## Summary

The integration testing framework provides:
- ✅ Complete system validation
- ✅ Cross-module intelligence testing
- ✅ Vector embedding validation
- ✅ Cache behavior verification
- ✅ Error handling coverage
- ✅ Isolated test environment
- ✅ Comprehensive fixtures
- ✅ CI/CD ready
