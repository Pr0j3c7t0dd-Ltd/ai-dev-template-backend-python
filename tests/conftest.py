import os
from pathlib import Path
from unittest.mock import AsyncMock, patch

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


# Create a mock Supabase client
class MockSupabaseClient:
    """Mock Supabase client for testing."""

    def __init__(self):
        self.mock_result = AsyncMock()
        self.mock_result.execute.return_value.data = []

    def table(self, _table_name):
        """Mock table method that returns self for chaining."""
        return self

    def select(self, *_args, **_kwargs):
        """Mock select method that returns self for chaining."""
        return self

    def limit(self, _limit):
        """Mock limit method that returns self for chaining."""
        return self

    async def execute(self):
        """Mock execute method that returns the mock result."""
        return self.mock_result.execute()


# Mock the get_supabase_client function
async def mock_get_supabase_client():
    """Return a mock Supabase client."""
    return MockSupabaseClient()


# Create a mock HTTP response for the health check
class MockResponse:
    """Mock HTTP response for testing."""

    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self.json_data = json_data or {}

    def json(self):
        """Return mock JSON data."""
        return self.json_data

    def raise_for_status(self):
        """Mock raise_for_status method."""
        if self.status_code >= 400:
            error_message = f"HTTP Error: {self.status_code}"
            raise Exception(error_message)


# Mock the httpx client for health checks
class MockAsyncClient:
    """Mock async HTTP client for testing."""

    async def __aenter__(self):
        return self

    async def __aexit__(self, _exc_type, _exc_val, _exc_tb):
        pass

    async def get(self, _url, _headers=None):
        """Mock GET request that returns a successful response."""
        # Return a success response that won't trigger an exception
        return MockResponse(200, {"data": "success"})


# Apply mocking before importing app
with (
    patch("src.config.Settings", return_value=MockSettings()),
    patch("src.config.get_settings", return_value=MockSettings()),
    patch(
        "src.database.supabase.get_supabase_client",
        side_effect=mock_get_supabase_client,
    ),
    patch("httpx.AsyncClient", return_value=MockAsyncClient()),
):
    # Mock the health check endpoint in tests to ensure it returns healthy
    from src.api.v1.health import router as health_router
    from src.main import app

    @patch.object(health_router.routes[0], "endpoint")
    async def mock_health_check(_):
        """Mock health check endpoint that always returns healthy."""
        return {
            "status": "healthy",
            "details": {"database": "connected", "services": "operational"},
        }


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
