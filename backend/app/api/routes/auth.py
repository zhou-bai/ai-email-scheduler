from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import AuthTokenResponse, LoginRequest, RegisterRequest

router = APIRouter(tags=["auth"])


@router.post(
    "/register", response_model=AuthTokenResponse, status_code=status.HTTP_201_CREATED
)
def register_user(
    payload: RegisterRequest, db: Session = Depends(get_db)
) -> AuthTokenResponse:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )

    user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
        is_active=True,
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    jwt_token = create_access_token(
        subject=str(user.id), additional_claims={"email": user.email, "role": user.role}
    )
    return AuthTokenResponse(access_token=jwt_token, user_id=user.id, email=user.email)


@router.post("/login", response_model=AuthTokenResponse)
def login_user(
    payload: LoginRequest, db: Session = Depends(get_db)
) -> AuthTokenResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive"
        )

    jwt_token = create_access_token(
        subject=str(user.id), additional_claims={"email": user.email, "role": user.role}
    )
    return AuthTokenResponse(access_token=jwt_token, user_id=user.id, email=user.email)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_user(current_user: User = Depends(get_current_user)) -> None:
    # TODO: Maybe Implement token revocation if using a token blacklist
    return None
