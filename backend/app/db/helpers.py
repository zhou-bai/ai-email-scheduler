from datetime import datetime
from typing import Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.oauth_token import OAuthToken
from app.models.user import User


def get_user(db: Session, user_key: str) -> Optional[User]:
    if user_key.isdigit():
        return db.query(User).filter(User.id == int(user_key)).first()
    return db.query(User).filter(User.email == user_key).first()


def get_or_create_user(db: Session, user_key: str) -> User:
    user = get_user(db, user_key)
    if user is None and "@" in user_key:
        user = User(email=user_key, hashed_password=None, is_active=True, role="user")
        db.add(user)
        db.commit()
        db.refresh(user)
    if user is None:
        raise RuntimeError(f"User not found: {user_key}")
    return user


def get_or_create_user_by_email(
    db: Session, email: str, full_name: Optional[str] = None
) -> User:
    """Find a user by email, create if not exists. Optionally update full_name.

    This is preferred for OAuth callbacks where Google returns the verified email.
    """
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        user = User(
            email=email,
            hashed_password=None,
            is_active=True,
            role="user",
            full_name=full_name,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    # Update name if provided and different
    if full_name and user.full_name != full_name:
        user.full_name = full_name
        db.commit()
        db.refresh(user)
    return user


def get_or_create_user_by_google_sub(
    db: Session,
    google_sub: str,
    email: str,
    full_name: Optional[str] = None,
) -> User:
    user = db.query(User).filter(User.google_sub == google_sub).first()
    if user is not None:
        should_update = False
        if user.email != email:
            user.email = email
            should_update = True
        if full_name and user.full_name != full_name:
            user.full_name = full_name
            should_update = True

        if should_update:
            db.commit()
            db.refresh(user)
        return user

    user = db.query(User).filter(User.email == email).first()
    if user is not None:
        user.google_sub = google_sub
        if full_name and user.full_name != full_name:
            user.full_name = full_name
        db.commit()
        db.refresh(user)
        return user

    user = User(
        google_sub=google_sub,
        email=email,
        hashed_password=None,
        full_name=full_name,
        is_active=True,
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_latest_token(db: Session, user_id: int) -> Optional[OAuthToken]:
    return (
        db.query(OAuthToken)
        .filter(OAuthToken.user_id == user_id)
        .order_by(desc(OAuthToken.expires_at))
        .first()
    )


def save_token(
    db: Session,
    user_id: int,
    access_token: str,
    refresh_token: str = "",
    expires_at: Optional[datetime] = None,
) -> OAuthToken:
    """Save OAuth tokens for a user, replacing any existing tokens."""
    # Remove existing tokens
    db.query(OAuthToken).filter(OAuthToken.user_id == user_id).delete()

    # Create new token
    token = OAuthToken(
        user_id=user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at,
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


def update_token(
    db: Session,
    token: OAuthToken,
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None,
    expires_at: Optional[datetime] = None,
) -> OAuthToken:
    if access_token is not None:
        token.access_token = access_token
    if refresh_token is not None:
        token.refresh_token = refresh_token
    if expires_at is not None:
        token.expires_at = expires_at
    db.commit()
    db.refresh(token)
    return token
