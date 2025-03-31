import pytest
from fastapi.testclient import TestClient

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
