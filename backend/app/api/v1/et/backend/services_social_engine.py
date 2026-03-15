"""
Module A: Automated Social Media Content Engine — Amazon Nova Edition
======================================================================
Content generation, scheduling, and feedback optimization.
All LLM calls use Amazon Nova 2 Lite via the Bedrock Converse API.
"""

import boto3
import json
import os
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import asyncio
from enum import Enum
from botocore.config import Config as BotoConfig

# ---------------------------------------------------------------------------
# Bedrock client for Nova
# ---------------------------------------------------------------------------
_bedrock_config = BotoConfig(
    region_name=os.environ.get('AWS_REGION', 'us-east-1'),
    retries={'max_attempts': 3, 'mode': 'adaptive'},
    read_timeout=120,
    connect_timeout=30,
)

_bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    config=_bedrock_config,
)

NOVA_TEXT_MODEL = os.environ.get('NOVA_TEXT_MODEL', 'amazon.nova-2-lite-v1:0')


class Platform(str, Enum):
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"


def _nova_generate(
    prompt: str,
    system_prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 300,
) -> Dict:
    """Call Nova 2 Lite via the Converse API and return parsed result."""
    try:
        response = _bedrock_runtime.converse(
            modelId=NOVA_TEXT_MODEL,
            messages=[
                {'role': 'user', 'content': [{'text': prompt}]}
            ],
            system=[{'text': system_prompt}],
            inferenceConfig={
                'temperature': temperature,
                'maxTokens': max_tokens,
            },
        )
        content = response['output']['message']['content'][0]['text']
        usage = response.get('usage', {})
        tokens_used = usage.get('inputTokens', 0) + usage.get('outputTokens', 0)
        return {'text': content.strip(), 'tokens_used': tokens_used}
    except Exception as e:
        return {'text': '', 'tokens_used': 0, 'error': str(e)}


class ContentGenerationService:
    """Service for AI-powered social media content generation using Nova."""

    def __init__(self):
        self.temperature = 0.7

    async def generate_caption(
        self,
        brand_keywords: List[str],
        platform: Platform,
        topic: str,
        tone: str,
        audience_persona: Dict,
        cta: str = None,
    ) -> Dict:
        """Generate platform-specific caption with Nova 2 Lite."""
        prompt = (
            f"Generate an engaging {platform.value} caption.\n"
            f"Topic: {topic}\nBrand keywords: {', '.join(brand_keywords)}\n"
            f"Tone: {tone}\nAudience: {audience_persona}\nCTA: {cta or 'Learn more'}"
        )

        result = await asyncio.to_thread(
            _nova_generate,
            prompt=prompt,
            system_prompt=(
                "You are a social media content expert. "
                "Generate engaging, platform-optimized captions."
            ),
            temperature=self.temperature,
            max_tokens=300,
        )

        if 'error' in result:
            return {"status": "error", "error": result['error'], "platform": platform.value}

        return {
            "status": "success",
            "caption": result['text'],
            "platform": platform.value,
            "tokens_used": result['tokens_used'],
        }

    async def generate_hashtags(
        self,
        brand_keywords: List[str],
        platform: Platform,
        topic: str,
    ) -> Dict:
        """Generate platform-optimized hashtags using Nova 2 Lite."""
        prompt = (
            f"Generate relevant, trending hashtags for a {platform.value} post.\n"
            f"Topic: {topic}\nBrand keywords: {', '.join(brand_keywords)}\n"
            "Return one hashtag per line."
        )

        result = await asyncio.to_thread(
            _nova_generate,
            prompt=prompt,
            system_prompt="You are a hashtag strategy expert. Generate relevant, trending hashtags.",
            temperature=0.5,
            max_tokens=100,
        )

        if 'error' in result:
            return {"status": "error", "error": result['error']}

        hashtags = [tag.strip() for tag in result['text'].split('\n') if tag.strip()]
        return {
            "status": "success",
            "hashtags": hashtags,
            "count": len(hashtags),
            "platform": platform.value,
        }

    async def generate_complete_content(
        self,
        brand_name: str,
        brand_keywords: List[str],
        tone: str,
        audience_persona: Dict,
        platforms: List[Platform],
        topic: str,
        campaign_goal: str = "engagement",
    ) -> Dict:
        """Generate complete content package for multiple platforms."""
        content_package = {
            "brand": brand_name,
            "topic": topic,
            "campaign_goal": campaign_goal,
            "generated_at": datetime.utcnow().isoformat(),
            "platforms": {},
        }

        for platform in platforms:
            caption_result = await self.generate_caption(
                brand_keywords=brand_keywords,
                platform=platform,
                topic=topic,
                tone=tone,
                audience_persona=audience_persona,
            )
            hashtags_result = await self.generate_hashtags(
                brand_keywords=brand_keywords,
                platform=platform,
                topic=topic,
            )
            content_package["platforms"][platform.value] = {
                "caption": caption_result.get("caption", ""),
                "hashtags": hashtags_result.get("hashtags", []),
                "status": "ready_for_review",
            }

        return content_package

    async def optimize_based_on_feedback(
        self,
        original_caption: str,
        engagement_metrics: Dict,
        brand_keywords: List[str],
        tone: str,
        topic: str,
        platform: Platform,
    ) -> Dict:
        """Refine content based on engagement performance using Nova 2 Lite."""
        analysis_prompt = (
            f"Analyze this {platform.value} post performance:\n"
            f"Caption: {original_caption}\n"
            f"Likes: {engagement_metrics.get('likes', 0)}, "
            f"Comments: {engagement_metrics.get('comments', 0)}, "
            f"Shares: {engagement_metrics.get('shares', 0)}, "
            f"CTR: {engagement_metrics.get('ctr', 0)}, "
            f"Engagement rate: {engagement_metrics.get('engagement_rate', 0)}\n"
            f"Brand keywords: {', '.join(brand_keywords)}\nTone: {tone}\n"
            "What worked and what should improve?"
        )

        analysis_result = await asyncio.to_thread(
            _nova_generate,
            prompt=analysis_prompt,
            system_prompt="You are a data-driven content strategist. Provide actionable improvements.",
            temperature=0.6,
            max_tokens=500,
        )

        if 'error' in analysis_result:
            return {"status": "error", "error": analysis_result['error']}

        analysis = analysis_result['text']

        refinement_prompt = (
            f"Rewrite this {platform.value} caption based on the analysis:\n"
            f"Original: {original_caption}\n"
            f"Analysis: {analysis}\n"
            f"Tone: {tone}, Topic: {topic}\n"
            "Return ONLY the improved caption."
        )

        refinement_result = await asyncio.to_thread(
            _nova_generate,
            prompt=refinement_prompt,
            system_prompt="You are a caption optimization expert. Improve captions while maintaining brand voice.",
            temperature=0.7,
            max_tokens=300,
        )

        return {
            "status": "success",
            "original_caption": original_caption,
            "refined_caption": refinement_result['text'],
            "analysis": analysis,
            "previous_engagement_rate": engagement_metrics.get("engagement_rate", 0),
            "improvement_suggestions": analysis,
        }


class SchedulingService:
    """Service for scheduling posts to social platforms."""

    OPTIMAL_POSTING_TIMES = {
        Platform.INSTAGRAM: [11, 13, 19],
        Platform.LINKEDIN: [8, 12, 17],
        Platform.TWITTER: [9, 14, 17],
        Platform.FACEBOOK: [13, 19],
        Platform.TIKTOK: [6, 10, 18],
    }

    def get_optimal_posting_time(self, platform: Platform) -> datetime:
        now = datetime.utcnow()
        optimal_hours = self.OPTIMAL_POSTING_TIMES.get(platform, [12])
        current_hour = now.hour

        for hour in optimal_hours:
            if hour > current_hour:
                return now.replace(hour=hour, minute=0, second=0, microsecond=0)

        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(hour=optimal_hours[0], minute=0, second=0, microsecond=0)

    async def schedule_post(
        self,
        platform: Platform,
        caption: str,
        hashtags: List[str],
        scheduled_time: datetime = None,
        image_url: str = None,
        video_url: str = None,
    ) -> Dict:
        if not scheduled_time:
            scheduled_time = self.get_optimal_posting_time(platform)

        post_data = {
            "platform": platform.value,
            "caption": caption,
            "hashtags": hashtags,
            "scheduled_time": scheduled_time.isoformat(),
            "image_url": image_url,
            "video_url": video_url,
            "status": "scheduled",
            "scheduled_at": datetime.utcnow().isoformat(),
        }

        return {
            "status": "success",
            "scheduled_post": post_data,
            "message": f"Post scheduled for {scheduled_time}",
        }


class PromptOptimizationService:
    """Service for continuous prompt optimization based on feedback."""

    def __init__(self):
        self.history = []

    def track_performance(self, post_id: str, metrics: Dict):
        self.history.append({
            "post_id": post_id,
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def get_performance_patterns(self, platform: Platform) -> Dict:
        platform_history = [
            h for h in self.history if h.get("platform") == platform.value
        ]
        if not platform_history:
            return {"status": "insufficient_data"}

        avg_engagement = (
            sum(h["metrics"].get("engagement_rate", 0) for h in platform_history)
            / len(platform_history)
        )
        return {
            "platform": platform.value,
            "avg_engagement_rate": avg_engagement,
            "total_posts": len(platform_history),
            "best_performing": max(
                platform_history, key=lambda x: x["metrics"].get("engagement_rate", 0)
            ),
            "patterns": "Performance patterns identified",
        }

    async def auto_refine_template(
        self, platform: Platform, brand_keywords: List[str], tone: str
    ) -> Dict:
        patterns = self.get_performance_patterns(platform)
        if patterns.get("status") == "insufficient_data":
            return {"status": "waiting_for_data", "message": "Need more data to optimize"}
        return {
            "status": "optimized",
            "platform": platform.value,
            "insights": patterns,
            "recommendation": "Continue with current strategy or test variations",
        }
