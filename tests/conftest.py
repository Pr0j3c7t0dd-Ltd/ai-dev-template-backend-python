import os
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# Set environment variables before any application imports
test_env_file = Path(__file__).parent.parent / ".env.test"
if test_env_file.exists():
    with open(test_env_file) as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key] = value


# Create mock settings before importing app
class MockSettings:
    """Mock settings for testing."""

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Modern FastAPI Server"

    # CORS Settings
    CORS_ORIGINS: list = ["http://localhost:3000"]  # Frontend URL

    # Environment Settings
    ENVIRONMENT: str = "development"

    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_TO_FILE: bool = False
    LOG_FILE_PATH: str = "logs/app.log"

    # Supabase Settings
    SUPABASE_URL: str = "https://test-supabase-url.com"
    SUPABASE_KEY: str = "test-supabase-key"
    SUPABASE_JWT_SECRET: str = "test-supabase-jwt-secret"  # noqa: S105


# Apply mocking before importing app
with (
    patch("src.config.Settings", return_value=MockSettings()),
    patch("src.config.get_settings", return_value=MockSettings()),
):
    from src.main import app


@pytest.fixture
def test_client():
    """Return a TestClient instance."""
    with TestClient(app) as client:
        # TestClient automatically checks if the app works
        yield client


@pytest.fixture
def test_token():
    """Return a test JWT token for authenticated endpoints."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXItaWQiLCJlbWFpbCI6InRlc3RAdGVzdC5jb20iLCJyb2xlIjoidXNlciJ9.this_is_a_test_token"
