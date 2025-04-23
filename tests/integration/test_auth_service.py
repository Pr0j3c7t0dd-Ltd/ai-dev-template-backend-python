"""
Integration tests for the AuthService.

These tests verify that the AuthService correctly integrates with Supabase.
Unlike functional tests that mock the AuthService, these tests use the real AuthService
but with test credentials and a test Supabase project.
"""

import os
import time

import pytest

from src.services.auth_service import AuthService
from src.utils.logger import logger


# Use a unique email for testing to avoid conflicts
def get_test_email():
    """Generate a unique test email."""
    timestamp = int(time.time())
    return f"test-{timestamp}@example.com"


@pytest.fixture
def auth_service():
    """Create a real AuthService instance for testing."""
    # The auth service will use the test environment variables
    # defined in .env.test file loaded by conftest.py
    return AuthService()


@pytest.mark.integration
async def test_sign_up_and_sign_in_flow(auth_service):
    """Test the complete sign-up and sign-in flow with a new user."""
    # Skip this test if we're not in a test environment
    if os.environ.get("ENVIRONMENT") != "test":
        pytest.skip("Skipping integration test in non-test environment")

    # Create a unique test email
    test_email = get_test_email()
    test_password = "TestPassword123!"  # noqa: S105

    # 1. Sign up a new user
    sign_up_result = await auth_service.sign_up(test_email, test_password)

    assert sign_up_result["success"] is True
    assert "message" in sign_up_result
    assert "check your email" in sign_up_result["message"].lower()

    # Note: In a real environment, we would verify the email here
    # but in tests we can use the unverified account

    # 2. Sign in with the new user
    sign_in_result = await auth_service.sign_in(test_email, test_password)

    assert sign_in_result["success"] is True
    assert "user" in sign_in_result
    assert sign_in_result["user"]["email"] == test_email
    assert "session" in sign_in_result
    assert "access_token" in sign_in_result["session"]
    assert "refresh_token" in sign_in_result["session"]

    # Store tokens for subsequent tests
    access_token = sign_in_result["session"]["access_token"]
    refresh_token = sign_in_result["session"]["refresh_token"]

    # 3. Verify the token works
    verify_result = await auth_service.verify_token(access_token)

    assert verify_result["success"] is True
    assert "user" in verify_result

    # 4. Test refresh token
    refresh_result = await auth_service.refresh_token(refresh_token)

    assert refresh_result["success"] is True
    assert "session" in refresh_result
    assert "access_token" in refresh_result["session"]

    # 5. Test sign out
    sign_out_result = await auth_service.sign_out(
        refresh_result["session"]["refresh_token"]
    )

    assert sign_out_result["success"] is True
    assert "message" in sign_out_result


@pytest.mark.integration
async def test_reset_password_flow(auth_service):
    """Test the password reset flow."""
    # Skip this test if we're not in a test environment
    if os.environ.get("ENVIRONMENT") != "test":
        pytest.skip("Skipping integration test in non-test environment")

    # Use an existing test account or create a new one
    test_email = "test-account-for-reset@example.com"
    test_password = "TestPassword123!"  # noqa: S105

    # Try to create the test account (may already exist)
    try:
        await auth_service.sign_up(test_email, test_password)
    except Exception as e:
        logger.warning(f"Could not create test account: {e}")

    # 1. Request password reset
    reset_result = await auth_service.reset_password_request(test_email)

    assert reset_result["success"] is True
    assert "message" in reset_result

    # Note: In a real test, we would need to intercept the email to get the reset token
    # For this test, we'll just verify the API call works correctly


@pytest.mark.integration
async def test_invalid_credentials(auth_service):
    """Test auth service with invalid credentials."""
    # Skip this test if we're not in a test environment
    if os.environ.get("ENVIRONMENT") != "test":
        pytest.skip("Skipping integration test in non-test environment")

    # 1. Try to sign in with invalid credentials
    sign_in_result = await auth_service.sign_in(
        "nonexistent@example.com", "WrongPassword123!"
    )

    assert sign_in_result["success"] is False
    assert "error" in sign_in_result

    # 2. Try to refresh with invalid token
    refresh_result = await auth_service.refresh_token("invalid-refresh-token")

    assert refresh_result["success"] is False
    assert "error" in refresh_result

    # 3. Try to verify invalid token
    verify_result = await auth_service.verify_token("invalid-access-token")

    assert verify_result["success"] is False
    assert "error" in verify_result


@pytest.mark.integration
async def test_jwt_decoding(auth_service):
    """Test JWT token decoding functionality."""
    # Skip this test if we're not in a test environment
    if os.environ.get("ENVIRONMENT") != "test":
        pytest.skip("Skipping integration test in non-test environment")

    # Create a unique test email
    test_email = get_test_email()
    test_password = "TestPassword123!"  # noqa: S105

    # 1. Sign up and sign in to get a valid token
    await auth_service.sign_up(test_email, test_password)
    sign_in_result = await auth_service.sign_in(test_email, test_password)

    assert sign_in_result["success"] is True

    # Get the access token
    access_token = sign_in_result["session"]["access_token"]

    # 2. Decode the JWT token
    decoded_token = auth_service.decode_jwt(access_token)

    assert decoded_token is not None
    assert "sub" in decoded_token  # Subject (user ID)
    assert "email" in decoded_token
    assert decoded_token["email"] == test_email
