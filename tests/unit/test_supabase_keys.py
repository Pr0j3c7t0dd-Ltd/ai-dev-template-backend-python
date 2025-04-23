"""Tests for Supabase key usage."""

from unittest.mock import MagicMock, patch

import pytest

from src.config.settings import Settings
from src.database.supabase import get_supabase_client


@pytest.fixture
def mock_settings():
    """Return mock settings with specific Supabase keys."""
    settings = MagicMock(spec=Settings)
    settings.SUPABASE_URL = "https://test-url.supabase.co"
    settings.SUPABASE_ANON_KEY = "test-anon-key"
    settings.SUPABASE_SERVICE_ROLE_KEY = "test-service-role-key"
    settings.SUPABASE_JWT_SECRET = "test-jwt-secret"  # noqa: S105
    return settings


@patch("src.database.supabase.create_client")
@patch("src.database.supabase.get_settings")
def test_supabase_client_uses_anon_key(
    mock_get_settings, mock_create_client, mock_settings
):
    """Test that Supabase client is created with anon key."""
    # Arrange
    mock_get_settings.return_value = mock_settings
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client

    # Act
    client = get_supabase_client()

    # Assert
    mock_create_client.assert_called_once_with(
        mock_settings.SUPABASE_URL, mock_settings.SUPABASE_ANON_KEY
    )
    assert client is mock_client


@patch("src.services.auth_service.get_settings")
def test_auth_service_uses_correct_keys(mock_get_settings, mock_settings):
    """Test that AuthService uses the correct Supabase keys."""
    # Arrange
    from src.services.auth_service import AuthService

    mock_get_settings.return_value = mock_settings

    # Act
    auth_service = AuthService()

    # Assert
    assert auth_service.supabase_anon_key == mock_settings.SUPABASE_ANON_KEY
    assert (
        auth_service.supabase_service_role_key
        == mock_settings.SUPABASE_SERVICE_ROLE_KEY
    )
    assert auth_service.headers["apikey"] == mock_settings.SUPABASE_ANON_KEY
    assert (
        auth_service.admin_headers["apikey"] == mock_settings.SUPABASE_SERVICE_ROLE_KEY
    )
