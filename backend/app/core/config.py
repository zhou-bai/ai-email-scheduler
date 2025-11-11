import secrets

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    FRONTEND_HOST: str = "http://localhost:5173"

    PROJECT_NAME: str = "AI Email Agent API"
    PROJECT_VERSION: str = "0.1.0"
    DEBUG: bool = True

    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    ALLOWED_ORIGINS: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="Allowed CORS origins",
    )

    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = Field(
        default="logs",
        description="Directory for log files",
    )


settings = Settings()  # type: ignore
