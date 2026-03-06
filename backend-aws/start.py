"""HiveMind AWS Backend - Health Check and Service Tests"""
import asyncio
import sys
from dotenv import load_dotenv
from config.aws_config import get_aws_settings
from services.aurora_service import get_db_connection
from services.cache_service import get_cache_service
from services.s3_service import get_s3_service
from services.bedrock_service import get_bedrock_service
from services.event_service import get_event_service

# Load environment variables
load_dotenv()
settings = get_aws_settings()

async def test_aurora():
    """Test Aurora PostgreSQL connection"""
    print("\n🔍 Testing Aurora PostgreSQL...")
    try:
        async with get_db_connection() as conn:
            result = await conn.fetchval('SELECT version()')
            print(f"✅ Aurora connected")
            print(f"   Host: {settings.DB_HOST}")
            print(f"   Database: {settings.DB_NAME}")
            print(f"   Version: {result[:60]}...")
            return True
    except Exception as e:
        print(f"❌ Aurora failed: {e}")
        return False

async def test_redis():
    """Test ElastiCache Redis connection"""
    print("\n🔍 Testing ElastiCache Redis...")
    try:
        cache = get_cache_service()
        pong = await cache.ping()
        await cache.set('health_check', {'status': 'ok', 'timestamp': 'now'}, ttl=60)
        result = await cache.get('health_check')
        print(f"✅ Redis connected")
        print(f"   Host: {settings.REDIS_HOST}")
        print(f"   Ping: {pong}")
        print(f"   Test data: {result}")
        return True
    except Exception as e:
        print(f"❌ Redis failed: {e}")
        return False

async def test_s3():
    """Test S3 upload and download"""
    print("\n🔍 Testing S3...")
    try:
        s3 = get_s3_service()
        test_key = "health_check/test.txt"
        test_data = b"HiveMind health check - EC2 in ap-south-1"
        
        # Upload
        url = await s3.upload_file(test_data, test_key, "text/plain")
        print(f"✅ S3 upload successful")
        print(f"   Bucket: {settings.S3_BUCKET}")
        print(f"   Region: {settings.AWS_REGION}")
        print(f"   URL: {url}")
        
        # Download
        downloaded = await s3.download_file(test_key)
        print(f"✅ S3 download successful")
        print(f"   Size: {len(downloaded)} bytes")
        print(f"   Content matches: {downloaded == test_data}")
        
        return True
    except Exception as e:
        print(f"❌ S3 failed: {e}")
        return False

async def test_bedrock():
    """Test Bedrock embedding and text generation"""
    print("\n🔍 Testing Bedrock...")
    try:
        bedrock = get_bedrock_service()
        
        # Test embedding
        test_text = "AI is transforming content creation"
        embedding = await bedrock.generate_embedding(test_text)
        print(f"✅ Bedrock embedding generated")
        print(f"   Region: {settings.AWS_REGION}")
        print(f"   Model: {settings.BEDROCK_MODEL_EMBEDDING}")
        print(f"   Dimensions: {len(embedding)}")
        print(f"   Sample: [{embedding[0]:.4f}, {embedding[1]:.4f}, ...]")
        
        # Test text generation
        prompt = "Write a one-sentence tagline for an AI content platform"
        text = await bedrock.generate_text(prompt, max_tokens=100)
        print(f"✅ Bedrock text generation successful")
        print(f"   Model: {settings.BEDROCK_MODEL_TEXT}")
        print(f"   Output: {text[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Bedrock failed: {e}")
        return False

async def test_eventbridge():
    """Test EventBridge event publishing"""
    print("\n🔍 Testing EventBridge...")
    try:
        events = get_event_service()
        await events.article_created(
            article_id=999,
            title="Health Check Article",
            content="Testing EventBridge from EC2",
            category="test"
        )
        print(f"✅ EventBridge event published")
        print(f"   Region: {settings.AWS_REGION}")
        print(f"   Event Bus: {settings.EVENT_BUS_NAME}")
        return True
    except Exception as e:
        print(f"❌ EventBridge failed: {e}")
        return False

async def main():
    """Run all service tests"""
    print("=" * 70)
    print("🚀 HiveMind AWS Backend - Service Health Check")
    print("   EC2 Instance in ap-south-1 VPC")
    print("=" * 70)
    
    results = {}
    results['aurora'] = await test_aurora()
    results['redis'] = await test_redis()
    results['s3'] = await test_s3()
    results['bedrock'] = await test_bedrock()
    results['eventbridge'] = await test_eventbridge()
    
    print("\n" + "=" * 70)
    print("📊 Health Check Summary")
    print("=" * 70)
    
    for service, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {service.upper()}: {'PASS' if status else 'FAIL'}")
    
    all_pass = all(results.values())
    
    print("\n" + "=" * 70)
    if all_pass:
        print("✅ All services operational - Backend ready!")
        print("=" * 70)
        return 0
    else:
        print("⚠️  Some services failed - Check configuration")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
