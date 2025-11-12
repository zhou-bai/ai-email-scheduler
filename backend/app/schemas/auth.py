from pydantic import BaseModel


class OAuthURLResponse(BaseModel):
    auth_url: str


class OAuthCallbackResponse(BaseModel):
    success: bool
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
