from fastapi import APIRouter

from app.api.routes import calendar, gmail, health, oauth, users

api_router = APIRouter()

api_router.include_router(prefix="/health", router=health.router)
api_router.include_router(prefix="/auth", router=oauth.router)
api_router.include_router(prefix="/users", router=users.router)
api_router.include_router(prefix="/gmail", router=gmail.router)
api_router.include_router(prefix="/calendar", router=calendar.router)

__all__ = ["api_router"]
