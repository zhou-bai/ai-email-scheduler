from pydantic import BaseModel


class UserProfileResponse(BaseModel):
    id: int
    email: str
    full_name: str | None
    role: str
    is_active: bool
    google_sub: str | None

    class Config:
        from_attributes = True
