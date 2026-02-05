"""
Voice API Routes
Handles voice input, STT, TTS, and AI processing
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import asyncio
import logging

from core.validators import VoiceInputValidator, validate_audio_file
from core.exceptions import ValidationError, VoiceProcessingError

logger = logging.getLogger(__name__)
router = APIRouter()

class VoiceResponse(BaseModel):
    success: bool
    transcribed_text: Optional[str] = None
    intent: Optional[str] = None
    response: str
    audio_url: Optional[str] = None
    processing_time: float
    error: Optional[str] = None

@router.post("/process-audio", response_model=VoiceResponse)
async def process_audio(
    audio: UploadFile = File(...),
    user_id: Optional[str] = "anonymous"
):
    """Process uploaded audio file through AI pipeline"""
    
    # Import here to avoid circular imports
    from main import ai_orchestrator, telemetry_manager
    
    try:
        # Validate audio file
        validate_audio_file(audio)
        
        # Read audio data
        audio_data = await audio.read()
        
        if len(audio_data) == 0:
            raise ValidationError("audio_file", "Empty audio file")
        
        await telemetry_manager.emit("audio_upload_received", {
            "user_id": user_id,
            "file_size": len(audio_data),
            "content_type": audio.content_type
        })
        
        # Process through AI orchestrator
        result = await ai_orchestrator.process_voice_input(audio_data, user_id)
        
        if result["success"]:
            return VoiceResponse(
                success=True,
                transcribed_text=result.get("transcribed_text"),
                intent=result.get("intent"),
                response=result.get("response", ""),
                processing_time=result.get("processing_time", 0.0)
            )
        else:
            return VoiceResponse(
                success=False,
                response="",
                processing_time=0.0,
                error=result.get("error")
            )
            
    except ValidationError as e:
        logger.warning(f"Validation error in audio processing: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except VoiceProcessingError as e:
        logger.error(f"Voice processing error: {e}")
        raise HTTPException(status_code=500, detail="Voice processing failed")
    except Exception as e:
        logger.error(f"Unexpected error in audio processing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/process-text", response_model=VoiceResponse)
async def process_text(query: VoiceInputValidator):
    """Process text input through AI pipeline (for testing)"""
    
    from main import ai_orchestrator, telemetry_manager
    
    try:
        await telemetry_manager.emit("text_input_received", {
            "user_id": query.user_id,
            "text_length": len(query.text),
            "language": query.language
        })
        
        # Mock audio data for text input
        mock_audio = query.text.encode('utf-8')
        
        # Process through orchestrator
        result = await ai_orchestrator.process_voice_input(mock_audio, query.user_id)
        
        if result["success"]:
            return VoiceResponse(
                success=True,
                transcribed_text=query.text,
                intent=result.get("intent"),
                response=result.get("response", ""),
                processing_time=result.get("processing_time", 0.0)
            )
        else:
            return VoiceResponse(
                success=False,
                response="",
                processing_time=0.0,
                error=result.get("error")
            )
            
    except ValidationError as e:
        logger.warning(f"Validation error in text processing: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except VoiceProcessingError as e:
        logger.error(f"Voice processing error: {e}")
        raise HTTPException(status_code=500, detail="Voice processing failed")
    except Exception as e:
        logger.error(f"Unexpected error in text processing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def voice_health():
    """Voice service health check"""
    from main import ai_orchestrator
    
    try:
        is_healthy = ai_orchestrator.is_initialized
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "services": {
                "stt": "mock_ready",  # TODO: Check actual STT service
                "tts": "mock_ready",  # TODO: Check actual TTS service
                "ai_orchestrator": "ready" if is_healthy else "not_ready"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")