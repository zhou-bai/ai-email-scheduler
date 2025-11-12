import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from urllib.parse import urlencode

import requests
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import get_latest_token, get_or_create_user, get_user, save_token, update_token


def build_auth_url(user_id: str, state: Optional[str] = None) -> str:
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise RuntimeError("Missing Google OAuth credentials")

    final_state = state or f"{user_id}:{secrets.token_urlsafe(16)}"
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(settings.GOOGLE_SCOPES),
        "access_type": "offline",
        "include_granted_scopes": "true",
        "prompt": "consent",
        "state": final_state,
    }
    return f"{settings.GOOGLE_AUTH_URI}?{urlencode(params)}"


def exchange_code_for_tokens(code: str) -> Tuple[str, Optional[str], Optional[datetime]]:
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    resp = requests.post(settings.GOOGLE_TOKEN_URI, data=data, timeout=10)
    resp.raise_for_status()
    payload = resp.json()

    access_token = payload.get("access_token")
    refresh_token = payload.get("refresh_token")
    expires_in = payload.get("expires_in")
    expiry = (datetime.utcnow() + timedelta(seconds=expires_in)) if expires_in else None

    if not access_token:
        raise RuntimeError(f"Failed to get access_token: {payload}")

    return access_token, refresh_token, expiry


def save_user_tokens(
    db: Session,
    user_key: str,
    access_token: str,
    refresh_token: str = "",
    expiry: Optional[datetime] = None,
) -> None:
    user = get_or_create_user(db, user_key)
    save_token(db, user.id, access_token, refresh_token, expiry)


def get_fresh_token(db: Session, user_key: str) -> str:
    user = get_user(db, user_key)
    if not user:
        raise RuntimeError("User not found")

    token = get_latest_token(db, user.id)
    if not token:
        raise RuntimeError("No tokens found")

    if token.expires_at and token.expires_at > datetime.utcnow():
        return token.access_token

    if not token.refresh_token:
        return token.access_token

    new_access, new_expiry = _refresh_token(token.refresh_token)
    update_token(db, token, access_token=new_access, expires_at=new_expiry)
    return new_access


def _refresh_token(refresh_token: str) -> Tuple[str, Optional[datetime]]:
    data = {
        "refresh_token": refresh_token,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "grant_type": "refresh_token",
    }
    resp = requests.post(settings.GOOGLE_TOKEN_URI, data=data, timeout=10)
    resp.raise_for_status()
    payload = resp.json()

    access_token = payload.get("access_token")
    expires_in = payload.get("expires_in")
    expiry = (datetime.utcnow() + timedelta(seconds=expires_in)) if expires_in else None

    if not access_token:
        raise RuntimeError(f"Failed to refresh token: {payload}")

    return access_token, expiry
