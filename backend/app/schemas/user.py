from pydantic import BaseModel, ConfigDict


class UserProfileResponse(BaseModel):
    id: int
    email: str
    full_name: str | None
    role: str
    is_active: bool
    google_sub: str | None
    model_config = ConfigDict(from_attributes=True)
