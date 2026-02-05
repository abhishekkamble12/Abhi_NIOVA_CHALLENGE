"""
LangGraph-based AI Orchestrator
Explicit flow: safety_check → intent_router → retrieve_context → generate_response → post_process
"""

from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import json
import logging

from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field, validator

from core.exceptions import AIOrchestrationError, VoiceProcessingError
from core.services import create_stt_service, create_tts_service, create_vector_db_service, create_llm_service
from config import settings

logger = logging.getLogger(__name__)

class ConversationState(BaseModel):
    """State passed through the AI orchestration pipeline"""
    user_input: str = ""
    audio_data: Optional[bytes] = None
    transcribed_text: Optional[str] = None
    safety_status: str = "pending"
    intent: Optional[str] = None
    confidence_score: float = 0.0
    context: Optional[Dict[str, Any]] = None
    response: Optional[str] = None
    audio_response: Optional[bytes] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_steps: list = Field(default_factory=list)
    
    @validator('confidence_score')
    def validate_confidence(cls, v):
        return max(0.0, min(1.0, v))  # Clamp between 0 and 1
    
    class Config:
        arbitrary_types_allowed = True

class AIOrchestrator:
    """Main AI orchestration engine using LangGraph"""
    
    def __init__(self, telemetry_manager):
        self.telemetry = telemetry_manager
        self.graph = None
        self.is_initialized = False
        
        # Initialize services
        self.stt_service = create_stt_service()
        self.tts_service = create_tts_service()
        self.vector_db_service = create_vector_db_service()
        self.llm_service = create_llm_service()
        
    async def initialize(self):
        """Initialize the LangGraph workflow"""
        try:
            self.graph = self._build_graph()
            self.is_initialized = True
            await self.telemetry.emit("orchestrator_initialized", {
                "nodes": ["safety_check", "intent_router", "retrieve_context", "generate_response", "post_process"],
                "settings": {
                    "max_response_length": settings.MAX_RESPONSE_LENGTH,
                    "processing_timeout": settings.PROCESSING_TIMEOUT,
                    "default_language": settings.DEFAULT_LANGUAGE
                }
            })
            logger.info("AI Orchestrator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI Orchestrator: {e}")
            raise AIOrchestrationError("Failed to initialize orchestrator", "initialization", {"error": str(e)})
    
    async def cleanup(self):
        """Cleanup orchestrator resources"""
        self.is_initialized = False
        logger.info("AI Orchestrator cleanup completed")
    
    def _build_graph(self) -> StateGraph:
        """Build the explicit AI orchestration graph"""
        workflow = StateGraph(ConversationState)
        
        # Add nodes
        workflow.add_node("safety_check", self._safety_check_node)
        workflow.add_node("intent_router", self._intent_router_node)
        workflow.add_node("retrieve_context", self._retrieve_context_node)
        workflow.add_node("generate_response", self._generate_response_node)
        workflow.add_node("post_process", self._post_process_node)
        
        # Define edges (explicit flow)
        workflow.set_entry_point("safety_check")
        workflow.add_edge("safety_check", "intent_router")
        workflow.add_edge("intent_router", "retrieve_context")
        workflow.add_edge("retrieve_context", "generate_response")
        workflow.add_edge("generate_response", "post_process")
        workflow.add_edge("post_process", END)
        
        return workflow.compile()
    
    async def process_voice_input(self, audio_data: bytes, user_id: str = "anonymous") -> Dict[str, Any]:
        """Main entry point for voice processing"""
        if not self.is_initialized:
            raise AIOrchestrationError("Orchestrator not initialized", "initialization")
            
        start_time = datetime.now()
        
        # Initialize state
        state = ConversationState(
            user_input="",
            audio_data=audio_data,
            metadata={"user_id": user_id, "start_time": start_time.isoformat()}
        )
        
        await self.telemetry.emit("voice_processing_started", {
            "user_id": user_id,
            "audio_size": len(audio_data)
        })
        
        try:
            # Run through the graph with timeout
            result = await asyncio.wait_for(
                self.graph.ainvoke(state.dict()),
                timeout=settings.PROCESSING_TIMEOUT
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            await self.telemetry.emit("voice_processing_completed", {
                "user_id": user_id,
                "processing_time": processing_time,
                "intent": result.get("intent"),
                "response_length": len(result.get("response", "")),
                "confidence_score": result.get("confidence_score", 0.0)
            })
            
            return {
                "success": True,
                "transcribed_text": result.get("transcribed_text"),
                "intent": result.get("intent"),
                "response": result.get("response"),
                "audio_response": result.get("audio_response"),
                "processing_time": processing_time,
                "confidence_score": result.get("confidence_score", 0.0)
            }
            
        except asyncio.TimeoutError:
            await self.telemetry.emit("voice_processing_timeout", {
                "user_id": user_id,
                "timeout": settings.PROCESSING_TIMEOUT
            })
            return {
                "success": False,
                "error": f"Processing timeout after {settings.PROCESSING_TIMEOUT} seconds"
            }
        except Exception as e:
            await self.telemetry.emit("voice_processing_error", {
                "user_id": user_id,
                "error": str(e),
                "error_type": type(e).__name__
            })
            logger.error(f"Voice processing failed for user {user_id}: {e}")
            return {
                "success": False,
                "error": "Processing failed. Please try again."
            }
    
    async def _safety_check_node(self, state: ConversationState) -> ConversationState:
        """Node 1: Safety and content filtering"""
        await self.telemetry.emit("node_safety_check_started", {"user_id": state.metadata.get("user_id")})

        # - Content filtering
        # - Threat detection
        # - Rural context validation
        
        # Mock implementation
        await asyncio.sleep(0.1)  # Simulate processing
        state.safety_status = "safe"
        
        await self.telemetry.emit("node_safety_check_completed", {
            "user_id": state.metadata.get("user_id"),
            "status": state.safety_status
        })
        
        return state
    
    async def _intent_router_node(self, state: ConversationState) -> ConversationState:
        """Node 2: Intent classification and routing"""
        await self.telemetry.emit("node_intent_router_started", {"user_id": state.metadata.get("user_id")})
        
        try:
            # STT: Convert audio to text if needed
            if state.audio_data and not state.transcribed_text:
                state.transcribed_text = await self.stt_service.transcribe(
                    state.audio_data, 
                    language=settings.DEFAULT_LANGUAGE
                )
            
            state.user_input = state.transcribed_text or state.user_input
            
            # Intent classification based on keywords and patterns
            intent, confidence = self._classify_intent(state.user_input)
            state.intent = intent
            state.confidence_score = confidence
            
            await self.telemetry.emit("node_intent_router_completed", {
                "user_id": state.metadata.get("user_id"),
                "intent": state.intent,
                "confidence": state.confidence_score,
                "transcribed_text": state.transcribed_text
            })
            
        except Exception as e:
            logger.error(f"Intent router failed: {e}")
            # Fallback to general query
            state.intent = "general_query"
            state.confidence_score = 0.5
            
        return state
    
    def _classify_intent(self, text: str) -> tuple[str, float]:
        """Classify user intent based on text analysis"""
        text_lower = text.lower()
        
        # Cybersecurity education keywords
        education_keywords = [
            "साइबर सुरक्षा", "cyber security", "cybersecurity", "सुरक्षा", "security",
            "जानकारी", "information", "सिखाना", "learn", "बताना", "tell"
        ]
        
        # Threat report keywords  
        threat_keywords = [
            "रिपोर्ट", "report", "शिकायत", "complaint", "धोखाधड़ी", "fraud",
            "स्कैम", "scam", "फिशिंग", "phishing", "हैक", "hack"
        ]
        
        # Emergency keywords
        emergency_keywords = [
            "तत्काल", "urgent", "emergency", "आपातकाल", "मदद", "help",
            "बचाओ", "save", "खतरा", "danger"
        ]
        
        # Calculate scores
        education_score = sum(1 for keyword in education_keywords if keyword in text_lower)
        threat_score = sum(1 for keyword in threat_keywords if keyword in text_lower)
        emergency_score = sum(1 for keyword in emergency_keywords if keyword in text_lower)
        
        # Determine intent with confidence
        if emergency_score > 0:
            return "emergency", min(0.9, 0.6 + emergency_score * 0.1)
        elif threat_score > 0:
            return "threat_report", min(0.9, 0.7 + threat_score * 0.1)
        elif education_score > 0:
            return "cybersecurity_education", min(0.9, 0.8 + education_score * 0.05)
        else:
            return "general_query", 0.5
    
    async def _retrieve_context_node(self, state: ConversationState) -> ConversationState:
        """Node 3: Context retrieval from vector DB"""
        await self.telemetry.emit("node_retrieve_context_started", {
            "user_id": state.metadata.get("user_id"),
            "intent": state.intent
        })
        
        try:
            # Retrieve relevant context from vector database
            context_results = await self.vector_db_service.similarity_search(
                query=state.user_input,
                top_k=3,
                filters={"language": settings.DEFAULT_LANGUAGE}
            )
            
            # Extract context information
            relevant_docs = [doc["content"] for doc in context_results]
            
            state.context = {
                "relevant_docs": relevant_docs,
                "context_results": context_results,
                "threat_level": self._assess_threat_level(state.intent),
                "regional_context": "rural_india"
            }
            
            await self.telemetry.emit("node_retrieve_context_completed", {
                "user_id": state.metadata.get("user_id"),
                "context_items": len(relevant_docs),
                "avg_relevance": sum(doc.get("relevance_score", 0) for doc in context_results) / max(len(context_results), 1)
            })
            
        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            # Fallback to minimal context
            state.context = {
                "relevant_docs": [],
                "threat_level": "unknown",
                "regional_context": "rural_india"
            }
        
        return state
    
    def _assess_threat_level(self, intent: str) -> str:
        """Assess threat level based on intent"""
        threat_levels = {
            "emergency": "high",
            "threat_report": "medium", 
            "cybersecurity_education": "low",
            "general_query": "low"
        }
        return threat_levels.get(intent, "unknown")
    
    async def _generate_response_node(self, state: ConversationState) -> ConversationState:
        """Node 4: AI response generation"""
        await self.telemetry.emit("node_generate_response_started", {
            "user_id": state.metadata.get("user_id"),
            "intent": state.intent
        })
        
        try:
            # Build prompt for LLM
            prompt = self._build_prompt(state)
            
            # Get context documents
            context_docs = state.context.get("relevant_docs", []) if state.context else []
            
            # Generate response using LLM
            response = await self.llm_service.generate_response(
                prompt=prompt,
                context=context_docs,
                max_tokens=settings.MAX_RESPONSE_LENGTH
            )
            
            state.response = response
            
            await self.telemetry.emit("node_generate_response_completed", {
                "user_id": state.metadata.get("user_id"),
                "response_length": len(state.response),
                "context_used": len(context_docs)
            })
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            # Fallback response
            fallback_responses = {
                "emergency": "तत्काल सहायता के लिए साइबर क्राइम हेल्पलाइन 1930 पर कॉल करें।",
                "threat_report": "आपकी रिपोर्ट दर्ज की गई है। हमारी टीम इसकी जांच करेगी।",
                "cybersecurity_education": "साइबर सुरक्षा के लिए मजबूत पासवर्ड का उपयोग करें।",
                "general_query": "मैं आपकी साइबर सुरक्षा संबंधी सहायता के लिए यहाँ हूँ।"
            }
            state.response = fallback_responses.get(state.intent, "मुझे समझ नहीं आया। कृपया दोबारा कहें।")
        
        return state
    
    def _build_prompt(self, state: ConversationState) -> str:
        """Build prompt for LLM based on state"""
        base_prompt = f"""
You are SatyaSetu, a helpful AI assistant for rural cybersecurity education in India.

User Query: {state.user_input}
Intent: {state.intent}
Language: {settings.DEFAULT_LANGUAGE}
Confidence: {state.confidence_score}

Context Information:
{chr(10).join(state.context.get("relevant_docs", [])[:2]) if state.context else "No specific context available"}

Instructions:
- Respond in {settings.DEFAULT_LANGUAGE} (Hindi) primarily
- Keep responses simple and practical for rural users
- Focus on actionable cybersecurity advice
- Be empathetic and supportive
- If it's an emergency, prioritize immediate help resources
"""
        return base_prompt
    
    async def _post_process_node(self, state: ConversationState) -> ConversationState:
        """Node 5: Post-processing and TTS"""
        await self.telemetry.emit("node_post_process_started", {
            "user_id": state.metadata.get("user_id")
        })
        
        try:
            # Generate audio response using TTS
            if state.response:
                state.audio_response = await self.tts_service.synthesize(
                    text=state.response,
                    language=settings.DEFAULT_LANGUAGE,
                    voice_id="rural_friendly"
                )
            
            # Add processing step tracking
            state.processing_steps = [
                "safety_check", "intent_router", "retrieve_context", 
                "generate_response", "post_process"
            ]
            
            await self.telemetry.emit("node_post_process_completed", {
                "user_id": state.metadata.get("user_id"),
                "has_audio": bool(state.audio_response),
                "final_response_length": len(state.response) if state.response else 0
            })
            
        except Exception as e:
            logger.error(f"Post-processing failed: {e}")
            # Continue without audio if TTS fails
            state.audio_response = None
        
        return state