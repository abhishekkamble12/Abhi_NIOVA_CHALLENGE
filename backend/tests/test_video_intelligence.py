import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Video, VideoScene, Caption, VideoStatus


@pytest.mark.integration
class TestVideoIntelligence:
    """Test video processing and intelligence features"""
    
    async def test_video_upload_flow(
        self,
        async_client: AsyncClient,
        test_user,
        auth_headers
    ):
        """Test video upload and metadata storage"""
        
        video_data = {
            "title": "Product Launch Video",
            "description": "Introducing our latest product",
            "file_path": "/uploads/videos/product_launch.mp4",
            "duration": 180.5,
            "resolution": "1920x1080",
            "fps": 30
        }
        
        response = await async_client.post(
            f"/api/v1/videos?user_id={test_user.id}",
            json=video_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["title"] == video_data["title"]
        assert data["duration"] == video_data["duration"]
        assert "id" in data
    
    async def test_video_embedding_generation(
        self,
        db_session: AsyncSession,
        test_video
    ):
        """Test video content embedding is generated"""
        
        await db_session.refresh(test_video)
        
        assert test_video.embedding is not None
        assert len(test_video.embedding) == 384
    
    async def test_scene_detection(
        self,
        db_session: AsyncSession,
        test_video
    ):
        """Test video scene detection and storage"""
        
        scenes = [
            VideoScene(
                video_id=test_video.id,
                start_time=0.0,
                end_time=10.5,
                description="Opening scene with logo",
                scene_type="intro",
                embedding=[0.4] * 384
            ),
            VideoScene(
                video_id=test_video.id,
                start_time=10.5,
                end_time=45.0,
                description="Product demonstration",
                scene_type="action",
                embedding=[0.5] * 384
            )
        ]
        
        db_session.add_all(scenes)
        await db_session.commit()
        
        # Verify scenes stored
        from sqlalchemy import select
        result = await db_session.execute(
            select(VideoScene).filter(VideoScene.video_id == test_video.id)
        )
        stored_scenes = result.scalars().all()
        
        assert len(stored_scenes) == 2
        assert all(scene.embedding is not None for scene in stored_scenes)
    
    async def test_caption_generation(
        self,
        db_session: AsyncSession,
        test_video
    ):
        """Test video caption generation and storage"""
        
        captions = [
            Caption(
                video_id=test_video.id,
                start_time=0.0,
                end_time=5.0,
                text="Welcome to our product demo",
                language="en",
                confidence=0.95
            ),
            Caption(
                video_id=test_video.id,
                start_time=5.0,
                end_time=10.0,
                text="Let me show you the key features",
                language="en",
                confidence=0.92
            )
        ]
        
        db_session.add_all(captions)
        await db_session.commit()
        
        # Verify captions stored
        from sqlalchemy import select
        result = await db_session.execute(
            select(Caption).filter(Caption.video_id == test_video.id)
        )
        stored_captions = result.scalars().all()
        
        assert len(stored_captions) == 2
        assert all(caption.text for caption in stored_captions)
    
    async def test_video_transcript_generation(
        self,
        async_client: AsyncClient,
        test_video,
        auth_headers
    ):
        """Test full video transcript generation"""
        
        response = await async_client.get(
            f"/api/v1/videos/{test_video.id}/transcript",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "transcript" in data or "captions" in data
    
    async def test_scene_similarity_search(
        self,
        async_client: AsyncClient,
        test_video,
        auth_headers
    ):
        """Test finding similar video scenes"""
        
        response = await async_client.get(
            f"/api/v1/video-scenes/search?query=product demo&video_id={test_video.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
    
    async def test_video_status_workflow(
        self,
        db_session: AsyncSession,
        test_user
    ):
        """Test video processing status workflow"""
        
        video = Video(
            user_id=test_user.id,
            title="Processing Test",
            file_path="/uploads/test.mp4",
            status=VideoStatus.UPLOADING
        )
        
        db_session.add(video)
        await db_session.commit()
        
        # Simulate processing
        video.status = VideoStatus.PROCESSING
        await db_session.commit()
        
        # Complete processing
        video.status = VideoStatus.READY
        video.transcript = "Generated transcript"
        await db_session.commit()
        
        await db_session.refresh(video)
        assert video.status == VideoStatus.READY
        assert video.transcript is not None
    
    async def test_video_insights_generation(
        self,
        async_client: AsyncClient,
        test_video,
        auth_headers
    ):
        """Test AI-generated video insights"""
        
        response = await async_client.get(
            f"/api/v1/videos/{test_video.id}/insights",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Insights should include summary, key moments, etc.
        assert "summary" in data or "insights" in data
