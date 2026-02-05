"""
External service integrations for SatyaSetu
STT, TTS, Vector DB, and LLM services
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod

from config import settings
from core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)

class STTService(ABC):
    """Abstract Speech-to-Text service"""
    
    @abstractmethod
    async def transcribe(self, audio_data: bytes, language: str = "hi") -> str:
        pass

class TTSService(ABC):
    """Abstract Text-to-Speech service"""
    
    @abstractmethod
    async def synthesize(self, text: str, language: str = "hi", voice_id: str = "default") -> bytes:
        pass

class VectorDBService(ABC):
    """Abstract Vector Database service"""
    
    @abstractmethod
    async def similarity_search(self, query: str, top_k: int = 5, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        pass

class LLMService(ABC):
    """Abstract Large Language Model service"""
    
    @abstractmethod
    async def generate_response(self, prompt: str, context: List[str] = None, max_tokens: int = 500) -> str:
        pass

# Mock implementations for development/demo

class MockSTTService(STTService):
    """Mock STT service for development"""
    
    async def transcribe(self, audio_data: bytes, language: str = "hi") -> str:
        # Simulate processing time
        await asyncio.sleep(0.5)
        
        # Mock transcriptions based on language
        mock_transcriptions = {
            "hi": "मुझे साइबर सुरक्षा के बारे में जानकारी चाहिए",
            "en": "I need information about cybersecurity",
            "bn": "আমার সাইবার নিরাপত্তা সম্পর্কে তথ্য দরকার"
        }
        
        # If audio is actually text (for text input), return it
        try:
            text_input = audio_data.decode('utf-8')
            if len(text_input) < 1000:  # Reasonable text length
                return text_input
        except:
            pass
        
        return mock_transcriptions.get(language, mock_transcriptions["hi"])

class MockTTSService(TTSService):
    """Mock TTS service for development"""
    
    async def synthesize(self, text: str, language: str = "hi", voice_id: str = "default") -> bytes:
        # Simulate processing time
        await asyncio.sleep(0.3)
        
        # Return mock audio data (in real implementation, this would be actual audio bytes)
        return f"MOCK_AUDIO_DATA:{text[:50]}...".encode('utf-8')

class MockVectorDBService(VectorDBService):
    """Mock Vector DB service for development"""
    
    def __init__(self):
        # Mock knowledge base for rural cybersecurity
        self.knowledge_base = [
            {
                "content": "साइबर सुरक्षा के मूल सिद्धांत: मजबूत पासवर्ड का उपयोग करें, संदिग्ध लिंक पर क्लिक न करें।",
                "category": "cybersecurity_basics",
                "language": "hi",
                "score": 0.95
            },
            {
                "content": "ग्रामीण क्षेत्रों में डिजिटल सुरक्षा: मोबाइल बैंकिंग के लिए सुरक्षित नेटवर्क का उपयोग करें।",
                "category": "rural_security",
                "language": "hi", 
                "score": 0.90
            },
            {
                "content": "फिशिंग अटैक से बचाव: अज्ञात ईमेल में दिए गए लिंक पर क्लिक न करें।",
                "category": "phishing_protection",
                "language": "hi",
                "score": 0.88
            },
            {
                "content": "Basic cybersecurity principles: Use strong passwords and avoid suspicious links.",
                "category": "cybersecurity_basics", 
                "language": "en",
                "score": 0.95
            }
        ]
    
    async def similarity_search(self, query: str, top_k: int = 5, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        # Simulate processing time
        await asyncio.sleep(0.2)
        
        # Simple keyword-based matching for demo
        query_lower = query.lower()
        results = []
        
        for doc in self.knowledge_base:
            score = 0.0
            
            # Simple scoring based on keyword matches
            if "साइबर" in query_lower or "cyber" in query_lower:
                if "cybersecurity" in doc["category"]:
                    score += 0.5
            
            if "सुरक्षा" in query_lower or "security" in query_lower:
                if "security" in doc["category"]:
                    score += 0.4
            
            if "ग्रामीण" in query_lower or "rural" in query_lower:
                if "rural" in doc["category"]:
                    score += 0.6
            
            if "फिशिंग" in query_lower or "phishing" in query_lower:
                if "phishing" in doc["category"]:
                    score += 0.7
            
            # Apply filters
            if filters:
                if "language" in filters and doc["language"] != filters["language"]:
                    continue
            
            if score > 0.1:  # Minimum relevance threshold
                results.append({**doc, "relevance_score": score})
        
        # Sort by relevance and return top_k
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:top_k]

class MockLLMService(LLMService):
    """Mock LLM service for development"""
    
    def __init__(self):
        # Pre-defined responses for different intents
        self.response_templates = {
            "cybersecurity_education": {
                "hi": "साइबर सुरक्षा के लिए: {context} इसके अलावा, हमेशा अपने डिवाइस को अपडेट रखें।",
                "en": "For cybersecurity: {context} Additionally, always keep your devices updated."
            },
            "threat_report": {
                "hi": "आपकी रिपोर्ट दर्ज की गई है। {context} हमारी टीम इसकी जांच करेगी।",
                "en": "Your report has been recorded. {context} Our team will investigate this."
            },
            "general_query": {
                "hi": "मैं आपकी साइबर सुरक्षा संबंधी सहायता के लिए यहाँ हूँ। {context}",
                "en": "I'm here to help with your cybersecurity needs. {context}"
            },
            "emergency": {
                "hi": "तत्काल सहायता के लिए साइबर क्राइम हेल्पलाइन 1930 पर कॉल करें। {context}",
                "en": "For immediate help, call the cyber crime helpline 1930. {context}"
            }
        }
    
    async def generate_response(self, prompt: str, context: List[str] = None, max_tokens: int = 500) -> str:
        # Simulate processing time
        await asyncio.sleep(0.8)
        
        # Extract intent and language from prompt (simplified)
        intent = "general_query"
        language = "hi"
        
        if "cybersecurity_education" in prompt:
            intent = "cybersecurity_education"
        elif "threat_report" in prompt:
            intent = "threat_report"
        elif "emergency" in prompt:
            intent = "emergency"
        
        if "language: en" in prompt or any(word in prompt.lower() for word in ["english", "help", "security"]):
            language = "en"
        
        # Build context string
        context_str = ""
        if context:
            context_str = " ".join(context[:2])  # Use first 2 context items
        
        # Get response template
        template = self.response_templates.get(intent, {}).get(language, 
            self.response_templates["general_query"]["hi"])
        
        response = template.format(context=context_str)
        
        # Truncate if too long
        if len(response) > max_tokens:
            response = response[:max_tokens-3] + "..."
        
        return response

# Service factory functions

def create_stt_service() -> STTService:
    """Create STT service based on configuration"""

    # if settings.STT_SERVICE == "whisper":
    #     return WhisperSTTService(settings.OPENAI_API_KEY)
    # elif settings.STT_SERVICE == "azure":
    #     return AzureSTTService(settings.AZURE_SPEECH_KEY)
    
    return MockSTTService()

def create_tts_service() -> TTSService:
    """Create TTS service based on configuration"""

    # if settings.TTS_SERVICE == "elevenlabs":
    #     return ElevenLabsTTSService(settings.ELEVENLABS_API_KEY)
    # elif settings.TTS_SERVICE == "azure":
    #     return AzureTTSService(settings.AZURE_SPEECH_KEY)
    
    return MockTTSService()

def create_vector_db_service() -> VectorDBService:
    """Create Vector DB service based on configuration"""

    # if settings.VECTOR_DB == "pinecone":
    #     return PineconeService(settings.PINECONE_API_KEY, settings.PINECONE_ENVIRONMENT)
    # elif settings.VECTOR_DB == "weaviate":
    #     return WeaviateService(settings.WEAVIATE_URL)
    
    return MockVectorDBService()

def create_llm_service() -> LLMService:
    """Create LLM service based on configuration"""

    # if settings.LLM_SERVICE == "openai":
    #     return OpenAIService(settings.OPENAI_API_KEY)
    # elif settings.LLM_SERVICE == "azure":
    #     return AzureOpenAIService(settings.AZURE_OPENAI_KEY)
    
    return MockLLMService()