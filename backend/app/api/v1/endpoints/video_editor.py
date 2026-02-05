from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.video import Video
from app.models.video_scene import VideoScene
from app.models.caption import Caption
from app.schemas.video_editor import VideoResponse, SceneResponse, CaptionResponse, ExportRequest
from app.services.video_processing import VideoProcessingService
from datetime import datetime
from typing import List
import aiofiles

router = APIRouter()

# ==================== VIDEO UPLOAD ====================

@router.post("/videos/upload", response_model=VideoResponse)
async def upload_video(
    title: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload raw video and start processing.
    
    Process:
    1. Save video file
    2. Extract duration
    3. Start background scene detection
    4. Start caption generation
    """
    
    # Mock file handling - in production, use S3/GCS
    file_path = f"uploads/videos/{file.filename}"
    
    # Create video record
    video = Video(
        user_id=1,  # Mock user_id
        title=title,
        file_url=file_path,
        duration=120.0,  # Mock duration - in production, extract with ffprobe
        processing_status="processing"
    )
    
    db.add(video)
    db.commit()
    db.refresh(video)

    # - Scene detection
    # - Caption generation
    # - Thumbnail selection
    
    return video

@router.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: int, db: Session = Depends(get_db)):
    """Get video details."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video

# ==================== SCENE DETECTION ====================

@router.post("/videos/{video_id}/detect-scenes")
async def detect_scenes(video_id: int, db: Session = Depends(get_db)):
    """
    Run AI scene detection on uploaded video.
    
    Detects:
    - Scene cuts
    - Transitions
    - Silence gaps
    - Key moments
    """
    
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Run scene detection using CV service
    detected_scenes = VideoProcessingService.detect_scenes(video.file_url, video.duration)
    
    # Save scenes to database
    for scene_data in detected_scenes:
        scene = VideoScene(
            video_id=video_id,
            start_time=scene_data["start_time"],
            end_time=scene_data["end_time"],
            scene_type=scene_data["scene_type"],
            confidence=scene_data["confidence"],
            description=scene_data["description"]
        )
        db.add(scene)
    
    db.commit()
    
    return {
        "video_id": video_id,
        "scenes_detected": len(detected_scenes),
        "scenes": detected_scenes
    }

@router.get("/videos/{video_id}/scenes", response_model=List[SceneResponse])
async def get_video_scenes(video_id: int, db: Session = Depends(get_db)):
    """Get detected scenes for a video."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    scenes = db.query(VideoScene).filter(VideoScene.video_id == video_id).all()
    return scenes

# ==================== CAPTION GENERATION ====================

@router.post("/videos/{video_id}/generate-captions")
async def generate_captions(video_id: int, language: str = "en", db: Session = Depends(get_db)):
    """
    Generate captions from video audio using speech-to-text.
    
    In production:
    - Use Whisper (OpenAI)
    - Use Azure Speech Services
    - Use Google Cloud Speech-to-Text
    """
    
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Extract audio
    audio_path = VideoProcessingService.extract_audio(video.file_url)
    
    # Generate captions
    caption_list = VideoProcessingService.generate_captions_from_audio(audio_path)
    
    # Save captions to database
    for caption_data in caption_list:
        caption = Caption(
            video_id=video_id,
            text=caption_data["text"],
            start_time=caption_data["start"],
            end_time=caption_data["end"],
            language=language
        )
        db.add(caption)
    
    db.commit()
    
    return {
        "video_id": video_id,
        "captions_generated": len(caption_list),
        "captions": caption_list
    }

@router.get("/videos/{video_id}/captions", response_model=List[CaptionResponse])
async def get_video_captions(video_id: int, db: Session = Depends(get_db)):
    """Get all captions for a video."""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    captions = db.query(Caption).filter(Caption.video_id == video_id).all()
    return captions

@router.put("/captions/{caption_id}")
async def edit_caption(caption_id: int, new_text: str, db: Session = Depends(get_db)):
    """Edit generated caption text."""
    caption = db.query(Caption).filter(Caption.id == caption_id).first()
    if not caption:
        raise HTTPException(status_code=404, detail="Caption not found")
    
    caption.text = new_text
    db.commit()
    db.refresh(caption)
    
    return {
        "message": "Caption updated",
        "caption": CaptionResponse.from_orm(caption)
    }

# ==================== THUMBNAIL SELECTION ====================

@router.post("/videos/{video_id}/select-thumbnail")
async def select_thumbnail(video_id: int, db: Session = Depends(get_db)):
    """
    AI-powered thumbnail selection using face/emotion detection.
    Optimized for click-through rate.
    """
    
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Get scenes for context
    scenes = db.query(VideoScene).filter(VideoScene.video_id == video_id).all()
    
    # Select best frame
    thumbnail = VideoProcessingService.select_thumbnail(video.file_url, [
        {
            "start_time": s.start_time,
            "end_time": s.end_time,
            "scene_type": s.scene_type
        }
        for s in scenes
    ])
    
    return {
        "video_id": video_id,
        "thumbnail": thumbnail,
        "preview_url": f"/thumbnails/video_{video_id}_frame_{int(thumbnail['frame_time'])}.jpg"
    }

# ==================== EXPORT & OPTIMIZATION ====================

@router.get("/export-presets")
async def get_export_presets():
    """Get platform-specific export presets."""
    return {
        "presets": VideoProcessingService.get_export_presets()
    }

@router.post("/videos/{video_id}/export")
async def export_video(video_id: int, export_request: ExportRequest, db: Session = Depends(get_db)):
    """
    Export video optimized for specific platform.
    
    Handles:
    - Aspect ratio conversion
    - Resolution optimization
    - Duration trimming
    - Caption embedding
    """
    
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    preset = export_request.preset
    
    # Mock export process
    export_config = {
        "video_id": video_id,
        "platform": preset.platform,
        "aspect_ratio": preset.aspect_ratio,
        "resolution": preset.resolution,
        "include_captions": export_request.apply_captions,
        "export_path": f"exports/video_{video_id}_{preset.platform}.mp4",
        "status": "queued"
    }
    
    return {
        "message": "Video export started",
        "export_config": export_config,
        "estimated_time": "2-5 minutes"
    }

@router.get("/videos/{video_id}/suggestions")
async def get_edit_suggestions(video_id: int, db: Session = Depends(get_db)):
    """
    Get AI-powered editing suggestions.
    Highlights best moments and suggests cuts.
    """
    
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    scenes = db.query(VideoScene).filter(VideoScene.video_id == video_id).all()
    
    # Get high-confidence scenes (likely key moments)
    key_moments = [s for s in scenes if s.confidence > 0.85]
    
    suggestions = {
        "video_id": video_id,
        "key_moments": [
            {
                "start_time": s.start_time,
                "end_time": s.end_time,
                "confidence": s.confidence,
                "recommendation": "Keep this segment - high engagement potential"
            }
            for s in key_moments
        ],
        "editing_tips": [
            "Trim silence gaps to tighten pacing",
            "Emphasize key moments with captions",
            "Add B-roll transitions between scenes",
            "Optimize first 3 seconds for retention"
        ]
    }
    
    return suggestions
