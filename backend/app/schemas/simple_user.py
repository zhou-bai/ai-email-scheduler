from pydantic import BaseModel, EmailStr


class SimpleUserCreate(BaseModel):
    email: EmailStr
    password: str
    nickname: str | None = None


class SimpleUserOut(BaseModel):
    id: int
    email: str
    nickname: str

    class Config:
        from_attributes = True


class SimpleUserLogin(BaseModel):
    email: EmailStr
    password: str