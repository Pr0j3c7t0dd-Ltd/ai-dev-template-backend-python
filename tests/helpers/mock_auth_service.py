"""
Helper to mock the auth service for testing.
"""

from unittest.mock import AsyncMock, patch


class MockAuthService:
    """Mock AuthService for testing."""

    def __init__(self):
        """Initialize the mock auth service with default responses."""
        self.sign_up_response = {
            "success": True,
            "message": "Account created successfully. Please check your email to confirm your account.",
        }

        self.sign_in_response = {
            "success": True,
            "user": {
                "id": "test-user-id",
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User",
                "avatar_url": None,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "email_verified": True,
            },
            "session": {
                "access_token": "mock-access-token",
                "refresh_token": "mock-refresh-token",
                "expires_at": 1672531200,
            },
        }

        self.sign_out_response = {
            "success": True,
            "message": "Successfully signed out",
        }

        self.reset_password_response = {
            "success": True,
            "message": "Password reset link sent to your email",
        }

        self.change_password_response = {
            "success": True,
            "message": "Password changed successfully",
        }

        self.verify_email_response = {
            "success": True,
            "message": "Email verified successfully",
        }

        self.refresh_token_response = {
            "success": True,
            "session": {
                "access_token": "new-mock-access-token",
                "refresh_token": "new-mock-refresh-token",
                "expires_at": 1672617600,
            },
        }

        self.verify_token_response = {
            "success": True,
            "user": {
                "id": "test-user-id",
                "email": "test@example.com",
            },
        }

        # Create async mock methods for all auth service methods
        self.sign_up = AsyncMock(return_value=self.sign_up_response)
        self.sign_in = AsyncMock(return_value=self.sign_in_response)
        self.sign_out = AsyncMock(return_value=self.sign_out_response)
        self.reset_password_request = AsyncMock(
            return_value=self.reset_password_response
        )
        self.change_password = AsyncMock(return_value=self.change_password_response)
        self.verify_email = AsyncMock(return_value=self.verify_email_response)
        self.refresh_token = AsyncMock(return_value=self.refresh_token_response)
        self.verify_token = AsyncMock(return_value=self.verify_token_response)
        self.oauth_initiate = AsyncMock(return_value="https://mocked-oauth-url.com")
        self.decode_jwt = AsyncMock(
            return_value={"sub": "test-user-id", "email": "test@example.com"}
        )

    def set_sign_up_error(self, error_message="Invalid email or password"):
        """Set sign up to return an error response."""
        self.sign_up.return_value = {
            "success": False,
            "error": error_message,
        }

    def set_sign_in_error(self, error_message="Invalid email or password"):
        """Set sign in to return an error response."""
        self.sign_in.return_value = {
            "success": False,
            "error": error_message,
        }

    def set_reset_password_error(self, error_message="User not found"):
        """Set reset password to return an error response."""
        self.reset_password_request.return_value = {
            "success": False,
            "error": error_message,
        }

    def set_change_password_error(self, error_message="Invalid token"):
        """Set change password to return an error response."""
        self.change_password.return_value = {
            "success": False,
            "error": error_message,
        }

    def set_verify_email_error(self, error_message="Invalid token"):
        """Set verify email to return an error response."""
        self.verify_email.return_value = {
            "success": False,
            "error": error_message,
        }

    def set_refresh_token_error(self, error_message="Invalid refresh token"):
        """Set refresh token to return an error response."""
        self.refresh_token.return_value = {
            "success": False,
            "error": error_message,
        }

    def set_verify_token_error(self, error_message="Invalid token"):
        """Set verify token to return an error response."""
        self.verify_token.return_value = {
            "success": False,
            "error": error_message,
        }


def patch_auth_service():
    """Return a patch for the AuthService class."""
    mock_service = MockAuthService()

    # Create a patcher for the AuthService instance
    # that will be used in dependency injection
    patcher = patch("src.api.v1.auth.auth_service", mock_service)

    return patcher, mock_service


def get_mock_auth_service():
    """Return a mock auth service for testing."""
    return MockAuthService()
