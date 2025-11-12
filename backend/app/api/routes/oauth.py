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
    uid = user_id or (state.split(":")[0] if state else "")
    if not uid:
        raise HTTPException(status_code=400, detail="Missing user_id/state")

    try:
        access_token, refresh_token, expiry = oauth.exchange_code_for_tokens(code)
        oauth.save_user_tokens(db, uid, access_token, refresh_token or "", expiry)
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
