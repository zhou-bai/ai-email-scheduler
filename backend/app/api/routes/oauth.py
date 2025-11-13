from urllib.parse import urlencode, urljoin, urlsplit, urlunsplit

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.logging_config import get_logger
from app.core.security import create_access_token
from app.schemas.auth import OAuthURLResponse
from app.services import oauth

router = APIRouter(tags=["oauth"])
logger = get_logger(__name__)


@router.get("/google/url", response_model=OAuthURLResponse)
def get_google_auth_url(
    state: str = Query("", description="Optional state parameter"),
) -> OAuthURLResponse:
    try:
        logger.info(f"Building Google OAuth URL, has_state: {bool(state)}")
        url = oauth.build_auth_url(user_id="", state=state or None)
        logger.debug("Google OAuth URL built successfully")
        return OAuthURLResponse(auth_url=url)
    except Exception as e:
        logger.error(
            f"Failed to build Google OAuth URL, has_state: {bool(state)}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/google/callback")
def google_oauth_callback(
    code: str,
    state: str = "",
    db: Session = Depends(get_db),
) -> RedirectResponse:
    try:
        logger.info(f"Handling Google OAuth callback, has_state: {bool(state)}")
        access_token, refresh_token, expiry = oauth.exchange_code_for_tokens(code)
        logger.debug(
            "Exchanged code for tokens",
            f"has_refresh: {bool(refresh_token)}, has_expiry: {bool(expiry)}",
        )

        userinfo = oauth.get_user_info(access_token)
        if not userinfo:
            logger.error("Google userinfo is empty")
            raise HTTPException(
                status_code=400,
                detail="Failed to fetch user info from Google",
            )

        try:
            user = oauth.ensure_user_from_google_by_sub(db, userinfo)
        except ValueError as e:
            logger.error(
                f"Invalid Google userinfo payload, keys: {list(userinfo.keys())}",
                exc_info=True,
            )
            raise HTTPException(status_code=400, detail=str(e))

        oauth.save_user_tokens_by_user_id(
            db, user.id, access_token, refresh_token or "", expiry
        )
        logger.info(
            f"Saved OAuth tokens for user, user_id: {user.id}, email: {user.email}"
        )

        jwt_token = create_access_token(
            subject=str(user.id),
            additional_claims={
                "email": user.email,
                "role": user.role,
            },
        )

        # TODO: change according to frontend handling design
        # Always redirect back to frontend with token in URL fragment
        success_path = "/auth/callback"
        frontend_base = settings.FRONTEND_HOST.rstrip("/")
        # Build destination using urllib.parse utilities
        dest_base = urljoin(frontend_base + "/", success_path.lstrip("/"))
        fragment = urlencode(
            {
                "token": jwt_token,
                "user_id": user.id,
                "email": user.email,
            }
        )
        parts = urlsplit(dest_base)
        redirect_url = urlunsplit(
            (parts.scheme, parts.netloc, parts.path, parts.query, fragment)
        )
        logger.info(
            f"Redirecting to frontend after OAuth, destination: {frontend_base}{success_path}, user_id: {user.id}",
        )
        return RedirectResponse(url=redirect_url, status_code=302)

    except HTTPException:
        # Re-raise explicit HTTP errors
        logger.warning(
            "OAuth callback raised HTTPException",
            extra={"has_state": bool(state)},
            exc_info=True,
        )
        raise
    except Exception:
        # TODO: change according to frontend error handling design
        # On error, redirect to a frontend error page (no sensitive details)
        error_path = "/auth/error"
        frontend_base = settings.FRONTEND_HOST.rstrip("/")
        logger.error(
            "Unexpected error during OAuth callback",
            f"has_state: {bool(state)}",
            exc_info=True,
        )
        dest_base = urljoin(frontend_base + "/", error_path.lstrip("/"))
        parts = urlsplit(dest_base)
        redirect_url = urlunsplit(
            (
                parts.scheme,
                parts.netloc,
                parts.path,
                parts.query,
                urlencode({"message": "oauth_failed"}),
            )
        )
        return RedirectResponse(url=redirect_url, status_code=302)
