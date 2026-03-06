"""Example Usage - No AWS SDK Required"""
import asyncio
from services.aurora_service import get_db_connection
from services.cache_service import get_cache_service
from services.s3_service import get_s3_service
from services.bedrock_service import get_bedrock_service
from services.event_service import get_event_service

async def example_article_workflow():
    """Complete article workflow without AWS SDK"""
    print("\n📝 Article Workflow")
    print("-" * 60)
    
    # 1. Store article in Aurora (direct asyncpg)
    async with get_db_connection() as conn:
        article_id = await conn.fetchval(
            """INSERT INTO articles (title, content, category) 
            VALUES ($1, $2, $3) RETURNING id""",
            "AI Trends 2024",
            "Artificial intelligence is transforming content creation...",
            "technology"
        )
    print(f"✅ Article stored in Aurora: {article_id}")
    
    # 2. Generate embedding (HTTP API)
    bedrock = get_bedrock_service()
    embedding = await bedrock.generate_embedding("AI Trends 2024")
    print(f"✅ Embedding generated: {len(embedding)} dimensions")
    
    # 3. Cache embedding (direct Redis)
    cache = get_cache_service()
    await cache.set_embedding("AI Trends 2024", embedding)
    print(f"✅ Embedding cached")
    
    # 4. Publish event (HTTP API)
    events = get_event_service()
    await events.article_created(article_id, "AI Trends 2024", "Content...", "technology")
    print(f"✅ Event published to EventBridge")

async def example_video_workflow():
    """Complete video workflow without AWS SDK"""
    print("\n🎥 Video Workflow")
    print("-" * 60)
    
    # 1. Upload to S3 (HTTP PUT with SigV4)
    s3 = get_s3_service()
    video_data = b"fake_video_data"
    video_url = await s3.upload_video(video_data, "demo.mp4")
    print(f"✅ Video uploaded to S3: {video_url}")
    
    # 2. Store metadata in Aurora
    async with get_db_connection() as conn:
        video_id = await conn.fetchval(
            """INSERT INTO videos (title, s3_url, duration) 
            VALUES ($1, $2, $3) RETURNING id""",
            "Product Demo",
            video_url,
            120.5
        )
    print(f"✅ Video metadata stored: {video_id}")
    
    # 3. Generate caption with Bedrock
    bedrock = get_bedrock_service()
    caption = await bedrock.generate_text("Create a short caption for a product demo video")
    print(f"✅ Caption generated: {caption[:50]}...")
    
    # 4. Publish event
    events = get_event_service()
    await events.video_uploaded(video_id, "videos/demo.mp4", 120.5)
    print(f"✅ Event published")

async def example_cache_patterns():
    """Cache patterns without AWS SDK"""
    print("\n💾 Cache Patterns")
    print("-" * 60)
    
    cache = get_cache_service()
    
    # Embedding cache
    embedding = [0.1] * 1536
    await cache.set_embedding("test text", embedding)
    cached = await cache.get_embedding("test text")
    print(f"✅ Embedding cached: {len(cached)} dimensions")
    
    # Feed cache
    articles = [{"id": 1, "title": "Article 1"}]
    await cache.set_feed(123, articles)
    feed = await cache.get_feed(123)
    print(f"✅ Feed cached: {len(feed)} articles")

async def example_bedrock_ai():
    """Bedrock AI without AWS SDK"""
    print("\n🤖 Bedrock AI")
    print("-" * 60)
    
    bedrock = get_bedrock_service()
    
    # Generate embedding
    embedding = await bedrock.generate_embedding("Content creation with AI")
    print(f"✅ Embedding: {len(embedding)} dimensions")
    
    # Generate text
    text = await bedrock.generate_text(
        "Write a LinkedIn post about AI in content creation",
        max_tokens=200
    )
    print(f"✅ Generated text: {text[:100]}...")

async def main():
    print("=" * 60)
    print("🚀 HiveMind Examples - No AWS SDK Required")
    print("=" * 60)
    
    await example_article_workflow()
    await example_video_workflow()
    await example_cache_patterns()
    await example_bedrock_ai()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed")
    print("=" * 60)
    print("\n🎉 No boto3, no AWS CLI, just direct connections!")

if __name__ == "__main__":
    asyncio.run(main())
