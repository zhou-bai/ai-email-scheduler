from fastapi import APIRouter, HTTPException, Query

from infrastructure.token_store import TokenStore
from services.oauth import build_google_auth_url, exchange_code_for_tokens

router = APIRouter(tags=["oauth"])
store = TokenStore()


@router.get("/google/url")
def get_google_auth_url(user_id: str = Query(..., description="你的系统内部用户ID")):
    try:
        url = build_google_auth_url(user_id)
        return {"auth_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/google/callback")
def google_oauth_callback(code: str, state: str = "", user_id: str = ""):
    uid = user_id or (state.split(":")[0] if state else "")
    if not uid:
        raise HTTPException(status_code=400, detail="Missing user_id/state")
    try:
        access_token, refresh_token, expiry = exchange_code_for_tokens(code)
        store.save_tokens(uid, access_token, refresh_token or "", expiry)
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
