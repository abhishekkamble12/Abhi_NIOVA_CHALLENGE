import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
import uuid

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.core.redis import init_redis, close_redis, redis_client
from app.services.vector_service import VectorService
from app.models import User, Brand, Article, Video


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for each test with rollback"""
    
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest.fixture
async def test_app(db_session):
    """Override database dependency in FastAPI app"""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield app
    
    app.dependency_overrides.clear()


@pytest.fixture
async def async_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing"""
    
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def redis_client_fixture():
    """Initialize Redis for tests"""
    await init_redis()
    yield redis_client
    await close_redis()


@pytest.fixture
def vector_service():
    """Create vector service instance"""
    return VectorService()


@pytest.fixture
async def test_user(db_session) -> User:
    """Create test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
        full_name="Test User",
        is_active=True,
        is_verified=True
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user


@pytest.fixture
async def test_brand(db_session, test_user) -> Brand:
    """Create test brand"""
    brand = Brand(
        user_id=test_user.id,
        name="Test Brand",
        description="A test brand for integration testing",
        industry="Technology",
        tone="professional",
        embedding=[0.1] * 1024  # Mock embedding
    )
    
    db_session.add(brand)
    await db_session.commit()
    await db_session.refresh(brand)
    
    return brand


@pytest.fixture
async def test_article(db_session) -> Article:
    """Create test article"""
    article = Article(
        title="AI Revolution in Content Creation",
        content="Artificial intelligence is transforming how we create content...",
        url="https://example.com/ai-revolution",
        source="TechNews",
        category="Technology",
        embedding=[0.2] * 1024  # Mock embedding
    )
    
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)
    
    return article


@pytest.fixture
async def test_video(db_session, test_user) -> Video:
    """Create test video"""
    video = Video(
        user_id=test_user.id,
        title="Product Demo Video",
        description="Demo of our latest product",
        file_path="/uploads/videos/test.mp4",
        duration=120.0,
        status="ready",
        embedding=[0.3] * 1024  # Mock embedding
    )
    
    db_session.add(video)
    await db_session.commit()
    await db_session.refresh(video)
    
    return video


@pytest.fixture
def auth_headers(test_user) -> dict:
    """Create authentication headers"""
    return {
        "Authorization": f"Bearer test_token_{test_user.id}",
        "X-User-ID": str(test_user.id)
    }


@pytest.fixture
def sample_embedding():
    """Generate sample embedding vector"""
    return [0.1] * 1024


@pytest.fixture
async def multiple_articles(db_session) -> list[Article]:
    """Create multiple test articles for search tests"""
    articles = [
        Article(
            title="Machine Learning Basics",
            content="Introduction to machine learning concepts...",
            url="https://example.com/ml-basics",
            category="Technology",
            embedding=[0.1 + i * 0.01 for i in range(1024)]
        )
        for i in range(5)
    ]
    
    db_session.add_all(articles)
    await db_session.commit()
    
    return articles
