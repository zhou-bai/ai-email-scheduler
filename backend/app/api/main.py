from fastapi import APIRouter

from app.api.routes import (
    auth, calendar, calendar_events, emails, gmail, health, oauth, users
)
from app.api.routes.simple_auth import router as simple_auth_router  # 新增这行！

api_router = APIRouter(prefix="")  # 加了 prefix

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(oauth.router, prefix="/auth", tags=["OAuth"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(gmail.router, prefix="/gmail", tags=["Gmail"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["Calendar"])
api_router.include_router(emails.router, prefix="/emails", tags=["Emails"])
api_router.include_router(calendar_events.router, prefix="/calendar-events", tags=["Calendar Events"])

# 新增：注册 Simple Auth 路由
api_router.include_router(simple_auth_router, prefix="", tags=["Simple Auth"])

__all__ = ["api_router"]