from urllib.parse import urlencode, urljoin, urlsplit, urlunsplit

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user_optional
from app.core.logging_config import get_logger
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.auth import OAuthURLResponse
from app.services import oauth

router = APIRouter(tags=["oauth"])
logger = get_logger(__name__)


@router.get("/google/url", response_model=OAuthURLResponse)
def get_google_auth_url(
    current_user: User | None = Depends(get_current_user_optional),
) -> OAuthURLResponse:
    """
    Get Google OAuth URL. Auto-detects mode:
    - No JWT: signup/login flow (state="signup:xxx")
    - With JWT: bind flow (state="bind:user_id:xxx")
    """
    try:
        import secrets

        if current_user:
            state = f"bind:{current_user.id}:{secrets.token_urlsafe(16)}"
            logger.info(f"Building bind OAuth URL, user_id={current_user.id}")
        else:
            state = f"signup:{secrets.token_urlsafe(16)}"
            logger.info("Building signup OAuth URL")

        url = oauth.build_auth_url(user_id="", state=state)
        return OAuthURLResponse(auth_url=url)
    except Exception as e:
        logger.error("Failed to build Google OAuth URL", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/google/callback")
def google_oauth_callback(
    code: str,
    state: str = "",
    db: Session = Depends(get_db),
) -> RedirectResponse:
    """
    Handle OAuth callback. Mode auto-detected from state:
    - state="signup:xxx" -> create/match user by google_sub
    - state="bind:user_id:xxx" -> link Google to existing user
    """
    try:
        logger.info(f"OAuth callback, state={state}")
        access_token, refresh_token, expiry = oauth.exchange_code_for_tokens(code)

        userinfo = oauth.get_user_info(access_token)
        if not userinfo or not userinfo.get("sub"):
            logger.error("Invalid Google userinfo")
            raise HTTPException(400, "Failed to fetch user info from Google")

        google_sub = userinfo["sub"]
        google_email = userinfo.get("email")

        parts = state.split(":", 2)
        mode = parts[0] if parts else "signup"

        if mode == "bind":
            if len(parts) < 2:
                raise HTTPException(400, "Invalid bind state format")

            try:
                user_id = int(parts[1])
            except ValueError:
                raise HTTPException(400, "Invalid user_id in state")

            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(404, "User not found")

            existing = db.query(User).filter(
                User.google_sub == google_sub, User.id != user.id
            ).first()
            if existing:
                raise HTTPException(409, "Google account already linked to another user")

            user.google_sub = google_sub
            if not user.email and google_email:
                user.email = google_email
            db.commit()
            logger.info(f"Linked Google to user_id={user.id}")
        else:
            try:
                user = oauth.ensure_user_from_google_by_sub(db, userinfo)
                logger.info(f"Signup/login user_id={user.id}")
            except ValueError as e:
                logger.error(f"Invalid userinfo: {list(userinfo.keys())}", exc_info=True)
                raise HTTPException(400, str(e))

        oauth.save_user_tokens_by_user_id(
            db, user.id, access_token, refresh_token or "", expiry
        )

        jwt_token = create_access_token(
            subject=str(user.id),
            additional_claims={"email": user.email, "role": user.role},
        )

        success_path = "/auth/callback"
        frontend_base = settings.FRONTEND_HOST.rstrip("/")
        dest_base = urljoin(frontend_base + "/", success_path.lstrip("/"))
        fragment = urlencode({
            "token": jwt_token,
            "user_id": user.id,
            "email": user.email,
            "mode": mode,
        })
        parts = urlsplit(dest_base)
        redirect_url = urlunsplit(
            (parts.scheme, parts.netloc, parts.path, parts.query, fragment)
        )
        logger.info(f"OAuth success, mode={mode}, user_id={user.id}")
        return RedirectResponse(url=redirect_url, status_code=302)

    except HTTPException:
        logger.warning("OAuth callback HTTPException", exc_info=True)
        raise
    except Exception:
        error_path = "/auth/error"
        frontend_base = settings.FRONTEND_HOST.rstrip("/")
        logger.error("Unexpected OAuth error", exc_info=True)
        dest_base = urljoin(frontend_base + "/", error_path.lstrip("/"))
        parts = urlsplit(dest_base)
        redirect_url = urlunsplit((
            parts.scheme, parts.netloc, parts.path, parts.query,
            urlencode({"message": "oauth_failed"}),
        ))
        return RedirectResponse(url=redirect_url, status_code=302)


@router.delete("/google/unlink", status_code=204)
def unlink_google_account(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
) -> None:
    """Unlink Google account from current user"""
    if not current_user:
        raise HTTPException(401, "Authentication required")

    if not current_user.google_sub:
        raise HTTPException(400, "No Google account linked")

    if not current_user.hashed_password:
        raise HTTPException(400, "Cannot unlink: please set a password first")

    current_user.google_sub = None
    db.commit()
    logger.info(f"Unlinked Google from user_id={current_user.id}")
    return None
