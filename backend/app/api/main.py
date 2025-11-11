from fastapi import APIRouter

from app.api.routes import health

api_router = APIRouter()

api_router.include_router(prefix="/health", router=health.router)

__all__ = ["api_router"]
