from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Modern FastAPI Server"

    # CORS Settings
    CORS_ORIGINS: list[str | AnyHttpUrl] = ["http://localhost:3000"]  # Frontend URL

    # Environment Settings
    ENVIRONMENT: str = "development"

    # Logging Settings
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_TO_FILE: bool = False
    LOG_FILE_PATH: str = "logs/app.log"

    # Supabase Settings
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_JWT_SECRET: str

    model_config = ConfigDict(case_sensitive=True, env_file=".env")


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached instance of the settings.
    """
    return Settings()
