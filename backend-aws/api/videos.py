"""Video Editor API Endpoints"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
from services.aurora_service import get_db_connection
from services.s3_service import get_s3_service
from services.bedrock_service import get_bedrock_service
from services.event_service import get_event_service
import uuid

router = APIRouter()

class ExportRequest(BaseModel):
    platform: str
    resolution: str
    format: str

@router.post("/videos/upload")
async def upload_video(file: UploadFile = File(...)):
    """Upload video to S3"""
    # Read file
    content = await file.read()
    
    # Upload to S3
    s3 = get_s3_service()
    filename = f"{uuid.uuid4()}_{file.filename}"
    url = await s3.upload_video(content, filename)
    
    # Store metadata
    async with get_db_connection() as conn:
        video_id = await conn.fetchval(
            """INSERT INTO videos (title, s3_url, filename, duration) 
            VALUES ($1, $2, $3, $4) RETURNING id""",
            file.filename, url, filename, 0.0
        )
    
    # Publish event
    events = get_event_service()
    await events.video_uploaded(video_id, filename, 0.0)
    
    return {"id": video_id, "url": url, "filename": filename}

@router.get("/videos/{video_id}")
async def get_video(video_id: int):
    """Get video by ID"""
    async with get_db_connection() as conn:
        video = await conn.fetchrow("SELECT * FROM videos WHERE id = $1", video_id)
    if not video:
        raise HTTPException(404, "Video not found")
    return dict(video)

@router.post("/videos/{video_id}/detect-scenes")
async def detect_scenes(video_id: int):
    """Detect scenes in video"""
    # Mock scene detection
    scenes = [
        {"start_time": 0.0, "end_time": 5.0, "confidence": 0.95},
        {"start_time": 5.0, "end_time": 10.0, "confidence": 0.92},
        {"start_time": 10.0, "end_time": 15.0, "confidence": 0.88}
    ]
    
    # Store scenes
    async with get_db_connection() as conn:
        for scene in scenes:
            await conn.execute(
                """INSERT INTO video_scenes (video_id, start_time, end_time, confidence) 
                VALUES ($1, $2, $3, $4)""",
                video_id, scene['start_time'], scene['end_time'], scene['confidence']
            )
    
    return {"scenes": scenes}

@router.get("/videos/{video_id}/scenes")
async def get_scenes(video_id: int):
    """Get video scenes"""
    async with get_db_connection() as conn:
        scenes = await conn.fetch(
            "SELECT * FROM video_scenes WHERE video_id = $1 ORDER BY start_time",
            video_id
        )
    return [dict(s) for s in scenes]

@router.post("/videos/{video_id}/generate-captions")
async def generate_captions(video_id: int, language: str = "en"):
    """Generate captions with Bedrock"""
    # Get video
    async with get_db_connection() as conn:
        video = await conn.fetchrow("SELECT * FROM videos WHERE id = $1", video_id)
    
    if not video:
        raise HTTPException(404, "Video not found")
    
    # Generate captions with Bedrock
    bedrock = get_bedrock_service()
    prompt = f"Generate 3 sample captions for a video titled: {video['title']}"
    captions_text = await bedrock.generate_text(prompt, max_tokens=200)
    
    # Store captions
    async with get_db_connection() as conn:
        caption_id = await conn.fetchval(
            """INSERT INTO video_captions (video_id, text, language, start_time, end_time) 
            VALUES ($1, $2, $3, $4, $5) RETURNING id""",
            video_id, captions_text, language, 0.0, 10.0
        )
    
    return {"id": caption_id, "text": captions_text}

@router.get("/videos/{video_id}/captions")
async def get_captions(video_id: int):
    """Get video captions"""
    async with get_db_connection() as conn:
        captions = await conn.fetch(
            "SELECT * FROM video_captions WHERE video_id = $1 ORDER BY start_time",
            video_id
        )
    return [dict(c) for c in captions]

@router.put("/captions/{caption_id}")
async def edit_caption(caption_id: int, new_text: str):
    """Edit caption"""
    async with get_db_connection() as conn:
        await conn.execute(
            "UPDATE video_captions SET text = $2 WHERE id = $1",
            caption_id, new_text
        )
    return {"status": "updated"}

@router.post("/videos/{video_id}/select-thumbnail")
async def select_thumbnail(video_id: int):
    """Select video thumbnail"""
    # Mock thumbnail generation
    s3 = get_s3_service()
    thumbnail_data = b"mock_thumbnail_data"
    url = await s3.upload_thumbnail(thumbnail_data, str(video_id))
    
    # Update video
    async with get_db_connection() as conn:
        await conn.execute(
            "UPDATE videos SET thumbnail_url = $2 WHERE id = $1",
            video_id, url
        )
    
    return {"thumbnail_url": url}

@router.get("/export-presets")
async def get_export_presets():
    """Get export presets"""
    return {
        "presets": [
            {"platform": "youtube", "resolution": "1080p", "format": "mp4"},
            {"platform": "instagram", "resolution": "1080x1080", "format": "mp4"},
            {"platform": "tiktok", "resolution": "1080x1920", "format": "mp4"}
        ]
    }

@router.post("/videos/{video_id}/export")
async def export_video(video_id: int, export_req: ExportRequest):
    """Export video"""
    # Get video
    async with get_db_connection() as conn:
        video = await conn.fetchrow("SELECT * FROM videos WHERE id = $1", video_id)
    
    if not video:
        raise HTTPException(404, "Video not found")
    
    # Mock export
    export_url = f"{video['s3_url']}_exported_{export_req.platform}.{export_req.format}"
    
    return {
        "export_url": export_url,
        "platform": export_req.platform,
        "resolution": export_req.resolution
    }

@router.get("/videos/{video_id}/suggestions")
async def get_suggestions(video_id: int):
    """Get AI suggestions for video"""
    # Get video
    async with get_db_connection() as conn:
        video = await conn.fetchrow("SELECT * FROM videos WHERE id = $1", video_id)
    
    if not video:
        raise HTTPException(404, "Video not found")
    
    # Generate suggestions with Bedrock
    bedrock = get_bedrock_service()
    prompt = f"Suggest 3 improvements for a video titled: {video['title']}"
    suggestions = await bedrock.generate_text(prompt, max_tokens=300)
    
    return {"suggestions": suggestions}
