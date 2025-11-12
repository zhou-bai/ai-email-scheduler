from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import oauth

router = APIRouter(tags=["oauth"])


@router.get("/google/url")
def get_google_auth_url(user_id: str = Query(..., description="Internal user ID")):
    try:
        url = oauth.build_auth_url(user_id)
        return {"auth_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/google/callback")
def google_oauth_callback(
    code: str,
    state: str = "",
    user_id: str = "",
    db: Session = Depends(get_db),
):
    # user_id is optional; we'll prefer Google userinfo's email to identify/create user
    try:
        access_token, refresh_token, expiry = oauth.exchange_code_for_tokens(code)

        # Fetch user info from Google to reliably determine the user's email
        userinfo = oauth.get_user_info(access_token)
        email = (userinfo or {}).get("email")

        # Fallback: if no email from Google (rare), use provided user_id if it looks like an email
        if not email and user_id and "@" in user_id:
            email = user_id

        # Last resort: try to parse from state prefix if it looks like an email
        if not email and state:
            candidate = state.split(":")[0]
            if "@" in candidate:
                email = candidate

        if not email:
            raise HTTPException(
                status_code=400,
                detail="Unable to resolve user email from Google userinfo/user_id/state",
            )

        # Ensure user exists (create/update from Google data)
        user = oauth.ensure_user_from_google(db, email=email, userinfo=userinfo)

        # Save tokens against this user
        oauth.save_user_tokens_by_user_id(
            db, user.id, access_token, refresh_token or "", expiry
        )
        return {"success": True, "email": email, "user_id": user.id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
