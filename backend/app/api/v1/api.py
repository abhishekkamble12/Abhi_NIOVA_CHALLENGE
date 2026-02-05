from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    races,
    helmets,
    performance,
    content,
    analytics,
    dashboard,
    social_media,
    news_feed_v2,
    orchestrator,
    video_editor
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(races.router, prefix="/races", tags=["races"])
api_router.include_router(helmets.router, prefix="/helmets", tags=["helmets"])
api_router.include_router(performance.router, prefix="/performance", tags=["performance"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

# AI Platform Modules
api_router.include_router(social_media.router, prefix="/social", tags=["social-media"])
api_router.include_router(news_feed_v2.router, prefix="/feed/real", tags=["real-news-feed"])
api_router.include_router(video_editor.router, prefix="/videos", tags=["video-editor"])
api_router.include_router(orchestrator.router, prefix="/orchestrator", tags=["orchestrator"])