from pydantic import BaseModel, EmailStr, ConfigDict


class SimpleUserCreate(BaseModel):
    email: EmailStr
    password: str
    nickname: str | None = None


class SimpleUserOut(BaseModel):
    id: int
    email: str
    nickname: str
    model_config = ConfigDict(from_attributes=True)


class SimpleUserLogin(BaseModel):
    email: EmailStr
    password: str