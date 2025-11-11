import secrets

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # project metadata
    FRONTEND_HOST: str = "http://localhost:5173"

    PROJECT_NAME: str = "AI Email Agent API"
    PROJECT_VERSION: str = "0.1.0"
    DEBUG: bool = True

    API_V1_STR: str = "/api/v1"

    # security config
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    ALLOWED_ORIGINS: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="Allowed CORS origins",
    )

    # logging config
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = Field(
        default="logs",
        description="Directory for log files",
    )

    # Google OAuth config
    GOOGLE_CLIENT_ID: str = Field(
        default="",
        description="Google OAuth 2.0 Client ID",
    )
    GOOGLE_CLIENT_SECRET: str = Field(
        default="",
        description="Google OAuth 2.0 Client Secret",
    )
    GOOGLE_OAUTH_REDIRECT_URI: str = Field(
        default="http://127.0.0.1:8000/api/v1/auth/google/callback",
        description="Google OAuth callback redirect URI",
    )

    # Google API Scopes
    GOOGLE_SCOPES: list[str] = Field(
        default=[
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.modify",
            "https://www.googleapis.com/auth/calendar.events",
            "https://www.googleapis.com/auth/userinfo.email",
        ],
        description="Google API OAuth scopes",
    )

    # Google OAuth URIs
    GOOGLE_TOKEN_URI: str = Field(
        default="https://oauth2.googleapis.com/token",
        description="Google OAuth token endpoint",
    )
    GOOGLE_AUTH_URI: str = Field(
        default="https://accounts.google.com/o/oauth2/v2/auth",
        description="Google OAuth authorization endpoint",
    )


settings = Settings()  # type: ignore
