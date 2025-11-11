from typing import Optional, Tuple
from urllib.parse import urlencode
import requests
from datetime import datetime, timedelta
import secrets

from app.core.config import settings
from infrastructure.token_store import TokenStore


def build_google_auth_url(user_id: str, state: Optional[str] = None) -> str:
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise RuntimeError(
            "Missing Google OAuth client credentials in environment variables."
        )
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


def exchange_code_for_tokens(
    code: str,
) -> Tuple[str, Optional[str], Optional[datetime]]:
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


def refresh_access_token(refresh_token: str) -> Tuple[str, Optional[datetime]]:
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
        raise RuntimeError(f"Failed to refresh access_token: {payload}")
    return access_token, expiry


def ensure_fresh_token(user_id: str, store: TokenStore) -> str:
    tokens = store.get_tokens(user_id)
    if not tokens:
        raise RuntimeError("No tokens found for user.")
    if tokens.expiry and tokens.expiry > datetime.utcnow():
        return tokens.access_token
    if not tokens.refresh_token:
        return tokens.access_token
    new_access_token, new_expiry = refresh_access_token(tokens.refresh_token)
    store.update_tokens(user_id, access_token=new_access_token, expiry=new_expiry)
    return new_access_token
