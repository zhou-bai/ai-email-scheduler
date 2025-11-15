from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.simple_user import SimpleUser
from app.schemas.simple_user import SimpleUserCreate, SimpleUserOut, SimpleUserLogin

router = APIRouter(prefix="/simple", tags=["Simple Auth"])


@router.post("/register", response_model=SimpleUserOut)
def register(user_data: SimpleUserCreate, db: Session = Depends(get_db)):
    # 检查邮箱是否已存在
    exists = db.query(SimpleUser).filter(SimpleUser.email == user_data.email).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # 创建新用户（密码明文存储，仅开发用）
    new_user = SimpleUser(
        email=user_data.email,
        password=user_data.password,  # 明文
        nickname=user_data.nickname or "User"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login")
def login(login_data: SimpleUserLogin, db: Session = Depends(get_db)):
    user = db.query(SimpleUser).filter(SimpleUser.email == login_data.email).first()
    if not user or user.password != login_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    return {"message": "Login successful", "user_id": user.id, "nickname": user.nickname}