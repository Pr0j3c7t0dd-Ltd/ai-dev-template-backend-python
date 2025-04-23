"""
Functional tests for authentication endpoints.
"""

from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from tests.helpers.mock_auth_service import patch_auth_service


@pytest.fixture
def auth_mock():
    """Fixture to provide a patched auth service."""
    patcher, mock_service = patch_auth_service()
    patcher.start()
    yield mock_service
    patcher.stop()


# Test Cases - Sign Up
@pytest.mark.functional
def test_sign_up_success(test_client: TestClient, auth_mock):
    """Test successful user registration."""
    # Given: A valid sign up request
    request_data = {
        "email": "user@example.com",
        "password": "Password123!",
    }

    # When: The sign up endpoint is called
    response = test_client.post("/api/v1/auth/sign-up", json=request_data)

    # Then: Verify the response
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["success"] is True
    assert "message" in data
    assert "created successfully" in data["message"]

    # Verify the mock was called with the correct arguments
    auth_mock.sign_up.assert_called_once_with(
        request_data["email"], request_data["password"]
    )


@pytest.mark.functional
def test_sign_up_invalid_password(test_client: TestClient):
    """Test sign up with invalid password."""
    # Given: A sign up request with an invalid password
    request_data = {
        "email": "user@example.com",
        "password": "short",  # Too short to meet requirements
    }

    # When: The sign up endpoint is called
    response = test_client.post("/api/v1/auth/sign-up", json=request_data)

    # Then: Verify the response
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data
    # Password validation error details should be in the response
    assert any("password" in str(error).lower() for error in data["detail"])


@pytest.mark.functional
def test_sign_up_invalid_email(test_client: TestClient):
    """Test sign up with invalid email."""
    # Given: A sign up request with an invalid email
    request_data = {
        "email": "not-an-email",  # Invalid email format
        "password": "Password123!",
    }

    # When: The sign up endpoint is called
    response = test_client.post("/api/v1/auth/sign-up", json=request_data)

    # Then: Verify the response
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data
    # Email validation error details should be in the response
    assert any("email" in str(error).lower() for error in data["detail"])


@pytest.mark.functional
def test_sign_up_failure(test_client: TestClient, auth_mock):
    """Test sign up with auth service failure."""
    # Given: Auth service is configured to return an error
    auth_mock.set_sign_up_error()

    request_data = {
        "email": "user@example.com",
        "password": "Password123!",
    }

    # When: The sign up endpoint is called
    response = test_client.post("/api/v1/auth/sign-up", json=request_data)

    # Then: Verify the response
    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = response.json()
    assert data["success"] is False
    assert "error" in data


# Test Cases - Sign In
@pytest.mark.functional
def test_sign_in_success(test_client: TestClient, auth_mock):
    """Test successful user sign in."""
    # Given: A valid sign in request
    request_data = {
        "email": "user@example.com",
        "password": "Password123!",
    }

    # When: The sign in endpoint is called
    response = test_client.post("/api/v1/auth/sign-in", json=request_data)

    # Then: Verify the response
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["success"] is True
    assert "user" in data
    assert "session" in data

    # Check that cookies are set
    cookies = response.cookies
    assert "access_token" in cookies
    assert "refresh_token" in cookies

    # Verify the mock was called with the correct arguments
    auth_mock.sign_in.assert_called_once_with(
        request_data["email"], request_data["password"]
    )


@pytest.mark.functional
def test_sign_in_invalid_credentials(test_client: TestClient, auth_mock):
    """Test sign in with invalid credentials."""
    # Given: Auth service is configured to return an error
    auth_mock.set_sign_in_error()

    request_data = {
        "email": "user@example.com",
        "password": "WrongPassword123!",
    }

    # When: The sign in endpoint is called
    response = test_client.post("/api/v1/auth/sign-in", json=request_data)

    # Then: Verify the response
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    data = response.json()
    assert data["success"] is False
    assert "error" in data


# Test Cases - Sign Out
@pytest.mark.functional
def test_sign_out_success(test_client: TestClient, auth_mock):
    """Test successful user sign out."""
    # Given: A valid refresh token cookie is set
    test_client.cookies.set("refresh_token", "mock-refresh-token")

    # When: The sign out endpoint is called
    response = test_client.post("/api/v1/auth/sign-out")

    # Then: Verify the response
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["success"] is True
    assert "message" in data
    assert "signed out" in data["message"]

    # Check that cookies are cleared
    assert "access_token" not in response.cookies
    assert "refresh_token" not in response.cookies

    # Verify the mock was called with the correct token
    auth_mock.sign_out.assert_called_once_with("mock-refresh-token")


@pytest.mark.functional
def test_sign_out_no_token(test_client: TestClient, auth_mock):
    """Test sign out without a refresh token cookie."""
    # Given: No refresh token cookie is set

    # When: The sign out endpoint is called
    response = test_client.post("/api/v1/auth/sign-out")

    # Then: Verify the response
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["success"] is True
    assert "message" in data

    # Verify the mock was not called since there was no token
    auth_mock.sign_out.assert_not_called()


# Test Cases - Reset Password
@pytest.mark.functional
def test_reset_password_success(test_client: TestClient, auth_mock):
    """Test successful password reset request."""
    # Given: A valid reset password request
    request_data = {
        "email": "user@example.com",
    }

    # When: The reset password endpoint is called
    response = test_client.post("/api/v1/auth/reset-password", json=request_data)

    # Then: Verify the response
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["success"] is True
    assert "message" in data
    assert "reset link sent" in data["message"]

    # Verify the mock was called with the correct email
    auth_mock.reset_password_request.assert_called_once_with(request_data["email"])


@pytest.mark.functional
def test_reset_password_failure(test_client: TestClient, auth_mock):
    """Test password reset with auth service failure."""
    # Given: Auth service is configured to return an error
    auth_mock.set_reset_password_error()

    request_data = {
        "email": "nonexistent@example.com",
    }

    # When: The reset password endpoint is called
    response = test_client.post("/api/v1/auth/reset-password", json=request_data)

    # Then: Verify the response
    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = response.json()
    assert data["success"] is False
    assert "error" in data


# Test Cases - Change Password
@pytest.mark.functional
def test_change_password_success(test_client: TestClient, auth_mock):
    """Test successful password change."""
    # Given: A valid change password request
    request_data = {
        "token": "valid-reset-token",
        "password": "NewPassword123!",
    }

    # When: The change password endpoint is called
    response = test_client.post("/api/v1/auth/change-password", json=request_data)

    # Then: Verify the response
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["success"] is True
    assert "message" in data
    assert "changed successfully" in data["message"]

    # Verify the mock was called with the correct arguments
    auth_mock.change_password.assert_called_once_with(
        request_data["token"], request_data["password"]
    )


@pytest.mark.functional
def test_change_password_invalid_token(test_client: TestClient, auth_mock):
    """Test change password with invalid token."""
    # Given: Auth service is configured to return an error
    auth_mock.set_change_password_error()

    request_data = {
        "token": "invalid-token",
        "password": "NewPassword123!",
    }

    # When: The change password endpoint is called
    response = test_client.post("/api/v1/auth/change-password", json=request_data)

    # Then: Verify the response
    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = response.json()
    assert data["success"] is False
    assert "error" in data


# Test Cases - Verify Email
@pytest.mark.functional
def test_verify_email_success(test_client: TestClient, auth_mock):
    """Test successful email verification."""
    # Given: Auth service returns successful verification

    # When: The verify email endpoint is called with a valid token
    response = test_client.get(
        "/api/v1/auth/verify-email/valid-token", follow_redirects=False
    )

    # Then: Verify the response is a redirect
    assert response.status_code in [HTTPStatus.FOUND, HTTPStatus.TEMPORARY_REDIRECT]
    location = response.headers.get("location")
    assert "email-verified" in location
    assert "success=true" in location

    # Verify the mock was called with the correct token
    auth_mock.verify_email.assert_called_once_with("valid-token")


@pytest.mark.functional
def test_verify_email_invalid_token(test_client: TestClient, auth_mock):
    """Test email verification with invalid token."""
    # Given: Auth service is configured to return an error
    auth_mock.set_verify_email_error()

    # When: The verify email endpoint is called with an invalid token
    response = test_client.get(
        "/api/v1/auth/verify-email/invalid-token", follow_redirects=False
    )

    # Then: Verify the response is a redirect with error
    assert response.status_code in [HTTPStatus.FOUND, HTTPStatus.TEMPORARY_REDIRECT]
    location = response.headers.get("location")
    assert "email-verified" in location
    assert "success=false" in location
    assert "error=" in location


# Test Cases - Refresh Token
@pytest.mark.functional
def test_refresh_token_success(test_client: TestClient, auth_mock):
    """Test successful token refresh."""
    # Given: A valid refresh token cookie is set
    test_client.cookies.set("refresh_token", "mock-refresh-token")

    # When: The refresh token endpoint is called
    response = test_client.post("/api/v1/auth/refresh")

    # Then: Verify the response
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["success"] is True
    assert "session" in data

    # Check new cookies are set
    cookies = response.cookies
    assert "access_token" in cookies
    assert "refresh_token" in cookies

    # Verify the mock was called with the correct token
    auth_mock.refresh_token.assert_called_once_with("mock-refresh-token")


@pytest.mark.functional
def test_refresh_token_missing(test_client: TestClient):
    """Test token refresh without a refresh token cookie."""
    # Given: No refresh token cookie is set

    # When: The refresh token endpoint is called
    response = test_client.post("/api/v1/auth/refresh")

    # Then: Verify the response
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    data = response.json()
    assert data["success"] is False
    assert "error" in data
    assert "Refresh token not found" in data["error"]


@pytest.mark.functional
def test_refresh_token_invalid(test_client: TestClient, auth_mock):
    """Test token refresh with an invalid refresh token."""
    # Given: Auth service is configured to return an error
    auth_mock.set_refresh_token_error()

    # Set an invalid refresh token cookie
    test_client.cookies.set("refresh_token", "invalid-refresh-token")

    # When: The refresh token endpoint is called
    response = test_client.post("/api/v1/auth/refresh")

    # Then: Verify the response
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    data = response.json()
    assert data["success"] is False
    assert "error" in data


# Test Cases - Verify Token
@pytest.mark.functional
def test_verify_token_success(test_client: TestClient, auth_mock):
    """Test successful token verification."""
    # Given: A verify token request with valid token
    request_data = {
        "token": "valid-oauth-token",
    }

    # When: The verify token endpoint is called
    response = test_client.post("/api/v1/auth/verify-token", json=request_data)

    # Then: Verify the response
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["success"] is True
    assert "user" in data

    # Verify the mock was called with the correct token
    auth_mock.verify_token.assert_called_once_with(request_data["token"])


@pytest.mark.functional
def test_verify_token_invalid(test_client: TestClient, auth_mock):
    """Test token verification with an invalid token."""
    # Given: Auth service is configured to return an error
    auth_mock.set_verify_token_error()

    request_data = {
        "token": "invalid-token",
    }

    # When: The verify token endpoint is called
    response = test_client.post("/api/v1/auth/verify-token", json=request_data)

    # Then: Verify the response
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    data = response.json()
    assert data["success"] is False
    assert "error" in data


# Test Cases - OAuth Login
@pytest.mark.functional
def test_oauth_login_redirect(test_client: TestClient, auth_mock):
    """Test OAuth login redirects to the provider."""
    # Given: Auth service returns OAuth URL

    # When: The OAuth login endpoint is called
    response = test_client.get("/api/v1/auth/oauth/google", follow_redirects=False)

    # Then: Verify the response is a redirect
    assert response.status_code in [HTTPStatus.FOUND, HTTPStatus.TEMPORARY_REDIRECT]
    location = response.headers.get("location")
    assert "mocked-oauth-url.com" in location

    # Verify the mock was called with the correct provider
    auth_mock.oauth_initiate.assert_called_once_with("google")
