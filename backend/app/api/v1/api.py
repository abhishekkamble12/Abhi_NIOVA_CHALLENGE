from fastapi import APIRouter, UploadFile, File
from typing import List
import os
import shutil

api_router = APIRouter()

# Create uploads directory for local testing
UPLOADS_DIR = "uploads/videos"
os.makedirs(UPLOADS_DIR, exist_ok=True)

@api_router.get("/")
async def api_root():
    return {"message": "API v1", "status": "active"}

# Social Media endpoints
@api_router.get("/social/brands")
async def list_brands():
    return []

@api_router.post("/social/brands")
async def create_brand(brand: dict):
    return {"id": 1, **brand}

@api_router.post("/social/generate/content")
async def generate_content(brand_id: int, platform: str):
    return {
        "id": 1,
        "caption": "Sample AI-generated caption",
        "hashtags": ["#AI", "#Tech"],
        "platform": platform
    }

# Feed endpoints
@api_router.get("/feed/feed/{user_id}")
async def get_feed(user_id: int, limit: int = 20):
    return {"feed": [], "status": "success"}

@api_router.post("/feed/track/behavior")
async def track_behavior(data: dict):
    return {"message": "Tracked"}

# Video endpoints - LOCAL PROCESSING (no S3)
@api_router.post("/videos/videos/upload")
async def upload_video(file: UploadFile = File(...)):
    # Save file locally instead of S3
    file_path = os.path.join(UPLOADS_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Return local file path for processing
    return {
        "id": 1,
        "filename": file.filename,
        "file_path": file_path,  # Local path instead of S3 URL
        "status": "uploaded",
        "storage": "local"  # Indicate local storage
    }

@api_router.post("/videos/videos/{video_id}/detect-scenes")
async def detect_scenes(video_id: int):
    # Process video from local file system
    # In production, this would use the file_path from upload response
    return {
        "scenes": [
            {"id": 1, "start_time": 0, "end_time": 5, "scene_type": "intro"},
            {"id": 2, "start_time": 5, "end_time": 15, "scene_type": "main"}
        ],
        "status": "processed",
        "storage": "local"  # Processed from local file
    }

@api_router.get("/videos/videos/{video_id}/suggestions")
async def get_suggestions(video_id: int):
    return {
        "suggestions": [
            {"type": "cut", "timestamp": 10, "confidence": 0.9},
            {"type": "transition", "timestamp": 20, "confidence": 0.8}
        ]
    }

@api_router.post("/videos/videos/{video_id}/captions")
async def generate_captions(video_id: int, language: str = "en"):
    return {
        "captions": [
            {"id": 1, "text": "Sample caption", "start_time": 0, "end_time": 5}
        ],
        "language": language
    }

@api_router.post("/videos/videos/{video_id}/select-thumbnail")
async def select_thumbnail(video_id: int, frame_number: int):
    return {
        "thumbnail_url": f"/uploads/thumbnail_{video_id}.jpg",
        "frame_number": frame_number
    }

@api_router.get("/videos/export-presets")
async def get_export_presets():
    return {
        "presets": [
            {
                "id": "instagram_reel",
                "name": "Instagram Reel",
                "aspect_ratio": "9:16",
                "resolution": "1080x1920",
                "max_duration": 90
            },
            {
                "id": "youtube_short",
                "name": "YouTube Short",
                "aspect_ratio": "9:16",
                "resolution": "1080x1920",
                "max_duration": 60
            },
            {
                "id": "tiktok",
                "name": "TikTok",
                "aspect_ratio": "9:16",
                "resolution": "1080x1920",
                "max_duration": 180
            }
        ]
    }

@api_router.post("/videos/videos/{video_id}/export")
async def export_video(video_id: int, preset_id: str):
    return {
        "export_id": 1,
        "status": "processing",
        "preset": preset_id,
        "estimated_time": 30
    }
