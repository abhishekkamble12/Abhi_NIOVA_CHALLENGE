"""EventBridge Service for EC2 in ap-south-1"""
import json
import httpx
from datetime import datetime
from typing import Dict, Any
from aws_requests_auth.aws_auth import AWSRequestsAuth
from config.aws_config import get_aws_settings

settings = get_aws_settings()

class EventService:
    def __init__(self):
        self.region = settings.AWS_REGION
        self.endpoint = f"https://events.{self.region}.amazonaws.com"
        self.event_bus = settings.EVENT_BUS_NAME
        
        self.auth = AWSRequestsAuth(
            aws_access_key=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_host=f"events.{self.region}.amazonaws.com",
            aws_region=self.region,
            aws_service='events'
        )
    
    async def publish_event(self, detail_type: str, detail: Dict[str, Any], source: str = "hivemind"):
        """Publish event to EventBridge"""
        url = f"{self.endpoint}/"
        
        payload = {
            "Entries": [{
                "Source": source,
                "DetailType": detail_type,
                "Detail": json.dumps(detail),
                "EventBusName": self.event_bus,
                "Time": datetime.utcnow().isoformat()
            }]
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url,
                json=payload,
                headers={
                    "Content-Type": "application/x-amz-json-1.1",
                    "X-Amz-Target": "AWSEvents.PutEvents"
                },
                auth=self.auth
            )
            response.raise_for_status()
    
    async def article_created(self, article_id: int, title: str, content: str, category: str):
        await self.publish_event('ArticleCreated', {
            'article_id': article_id,
            'title': title,
            'content': content,
            'category': category,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def post_created(self, post_id: int, platform: str, content: str):
        await self.publish_event('PostCreated', {
            'post_id': post_id,
            'platform': platform,
            'content': content,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def video_uploaded(self, video_id: int, s3_key: str, duration: float):
        await self.publish_event('VideoUploaded', {
            'video_id': video_id,
            's3_key': s3_key,
            'duration': duration,
            'timestamp': datetime.utcnow().isoformat()
        })

def get_event_service() -> EventService:
    return EventService()
