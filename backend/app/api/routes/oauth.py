from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token
from app.schemas.auth import OAuthCallbackResponse, OAuthURLResponse
from app.services import oauth

router = APIRouter(tags=["oauth"])


@router.get("/google/url", response_model=OAuthURLResponse)
def get_google_auth_url(
    state: str = Query("", description="Optional state parameter"),
) -> OAuthURLResponse:
    try:
        url = oauth.build_auth_url(user_id="", state=state or None)
        return OAuthURLResponse(auth_url=url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/google/callback", response_model=OAuthCallbackResponse)
def google_oauth_callback(
    code: str,
    state: str = "",
    db: Session = Depends(get_db),
) -> OAuthCallbackResponse:
    try:
        access_token, refresh_token, expiry = oauth.exchange_code_for_tokens(code)

        userinfo = oauth.get_user_info(access_token)
        if not userinfo:
            raise HTTPException(
                status_code=400,
                detail="Failed to fetch user info from Google",
            )

        try:
            user = oauth.ensure_user_from_google_by_sub(db, userinfo)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        oauth.save_user_tokens_by_user_id(
            db, user.id, access_token, refresh_token or "", expiry
        )

        jwt_token = create_access_token(
            subject=str(user.id),
            additional_claims={
                "email": user.email,
                "role": user.role,
            },
        )

        return OAuthCallbackResponse(
            success=True,
            access_token=jwt_token,
            token_type="bearer",
            user_id=user.id,
            email=user.email,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
