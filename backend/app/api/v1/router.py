from fastapi import APIRouter

from app.api.v1.endpoints import brands, articles

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(brands.router)
api_router.include_router(articles.router)
