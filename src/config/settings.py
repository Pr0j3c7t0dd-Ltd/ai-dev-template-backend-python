from typing import List, Literal
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl

class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Modern FastAPI Server"
    
    # CORS Settings
    CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:3000"]  # Frontend URL
    
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
    
    class Config:
        case_sensitive = True
        env_file = ".env" 