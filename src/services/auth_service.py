"""Authentication service for Supabase integration."""

from typing import Any, Optional

import httpx
from jose import jwt
from pydantic import EmailStr

from src.config.settings import get_settings
from src.utils.logger import logger


class AuthService:
    """Service for handling authentication operations via Supabase."""

    def __init__(self):
        self.settings = get_settings()
        self.supabase_url = self.settings.SUPABASE_URL
        self.supabase_key = self.settings.SUPABASE_KEY
        self.supabase_jwt_secret = self.settings.SUPABASE_JWT_SECRET
        self.headers = {
            "apikey": self.supabase_key,
            "Content-Type": "application/json",
        }

    async def sign_up(self, email: EmailStr, password: str) -> dict[str, Any]:
        """Register a new user with email and password."""
        url = f"{self.supabase_url}/auth/v1/signup"

        logger.debug(f"Attempting signup for email: {email}")
        logger.debug(f"Request URL: {url}")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Log the request payload (omitting password)
                logger.debug(
                    f"Signup request payload: {{'email': '{email}', 'password': '********'}}"
                )
                logger.debug(f"Request headers: {self.headers}")

                response = await client.post(
                    url,
                    json={"email": email, "password": password},
                    headers=self.headers,
                )

                # Log the response status and headers
                logger.debug(f"Signup response status: {response.status_code}")
                logger.debug(f"Signup response headers: {dict(response.headers)}")

                if response.status_code == 200:
                    logger.info(f"Signup successful for email: {email}")
                    return {
                        "success": True,
                        "message": "Account created successfully. Please check your email to confirm your account.",
                    }

                # Handle error responses with detailed logging
                try:
                    error_data = response.json()
                    error_code = error_data.get("code", "unknown_code")
                    error_msg = error_data.get("message", "Unknown error during signup")
                    error_details = error_data.get("details", {})

                    # Extract additional error information
                    supabase_error_code = error_data.get("error_code")
                    supabase_msg = error_data.get("msg")
                    error_id = error_data.get("error_id")

                    # Create more detailed error info
                    detailed_error = error_msg
                    if supabase_msg:
                        detailed_error = supabase_msg

                    # Log all error details
                    logger.error(
                        f"Signup error for email {email}: Code: {error_code}, Message: {detailed_error}"
                    )
                    logger.error(f"Error details: {error_details}")
                    logger.error(f"Full error response: {error_data}")

                    # Provide a more specific error message to the user
                    user_error_msg = self._get_user_friendly_error_message(
                        supabase_error_code or error_code, detailed_error
                    )

                    return {
                        "success": False,
                        "error": user_error_msg,
                        "error_code": supabase_error_code or error_code,
                        "details": {"message": detailed_error, "error_id": error_id},
                    }
                except ValueError:
                    # If JSON parsing fails, log the raw response
                    raw_response = response.text[:1000]  # Limit to 1000 chars
                    logger.error(
                        f"Failed to parse error response. Status: {response.status_code}, Raw response: {raw_response}"
                    )
                    return {
                        "success": False,
                        "error": f"Unexpected response from authentication service (HTTP {response.status_code})",
                        "error_code": "parse_error",
                    }

        except httpx.TimeoutException:
            logger.error(f"Timeout during signup request for email: {email}")
            return {
                "success": False,
                "error": "The authentication service is taking too long to respond. Please try again later.",
                "error_code": "timeout",
            }
        except httpx.RequestError as e:
            logger.error(
                f"HTTP request error during signup for email {email}: {str(e)}",
                exc_info=True,
            )
            return {
                "success": False,
                "error": "Failed to connect to the authentication service. Please check your network connection and try again.",
                "error_code": "connection_error",
            }
        except Exception as e:
            logger.error(
                f"Unexpected exception during signup for email {email}: {str(e)}",
                exc_info=True,
            )
            return {
                "success": False,
                "error": "An unexpected error occurred. Please try again later.",
                "error_code": "unexpected_error",
            }

    def _get_user_friendly_error_message(
        self, error_code: str, original_message: str
    ) -> str:
        """Convert error codes to user-friendly messages."""
        error_messages = {
            "user_already_registered": "This email is already registered. Please try signing in or use a different email.",
            "invalid_email": "The email address format is invalid.",
            "weak_password": "The password does not meet security requirements.",
            "email_taken": "This email is already in use. Please try a different one.",
            "network_error": "Network connection error. Please check your internet connection and try again.",
            "unexpected_failure": "Our database encountered an error while creating your account. This might be due to a temporary issue or a configuration problem. Please try again later or contact support if the problem persists.",
            "database_error": "Database error encountered. This could be due to a temporary issue or a configuration problem. Please try again later.",
            "500": "The server encountered an internal error. Please try again later or contact support if the problem persists.",
        }

        # Check if original message contains database specific errors
        if "database error" in original_message.lower():
            return "Database error encountered. This could be due to a temporary issue or a unique constraint violation. Please try again with a different email address."

        # Return friendly message if available, otherwise return the original message
        return error_messages.get(error_code, original_message)

    async def sign_in(self, email: EmailStr, password: str) -> dict[str, Any]:
        """Authenticate a user with email and password."""
        url = f"{self.supabase_url}/auth/v1/token?grant_type=password"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={"email": email, "password": password},
                    headers=self.headers,
                )

                if response.status_code == 200:
                    auth_data = response.json()
                    user = auth_data.get("user", {})

                    return {
                        "success": True,
                        "user": {
                            "id": user.get("id"),
                            "email": user.get("email"),
                            "first_name": user.get("user_metadata", {}).get(
                                "first_name"
                            ),
                            "last_name": user.get("user_metadata", {}).get("last_name"),
                            "avatar_url": user.get("user_metadata", {}).get(
                                "avatar_url"
                            ),
                            "created_at": user.get("created_at"),
                            "updated_at": user.get("updated_at"),
                            "email_verified": user.get("email_confirmed_at")
                            is not None,
                        },
                        "session": {
                            "access_token": auth_data.get("access_token"),
                            "refresh_token": auth_data.get("refresh_token"),
                            "expires_at": auth_data.get("expires_at"),
                        },
                    }
                error_data = response.json()
                error_msg = error_data.get("message", "Invalid email or password")
                logger.error(f"Sign in error: {error_msg}")
                return {"success": False, "error": error_msg}

        except Exception as e:
            logger.error(f"Exception during sign in: {str(e)}")
            return {
                "success": False,
                "error": "Service unavailable. Please try again later.",
            }

    async def sign_out(self, refresh_token: str) -> dict[str, Any]:
        """Sign out the current user by invalidating their session."""
        url = f"{self.supabase_url}/auth/v1/logout"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, json={"refresh_token": refresh_token}, headers=self.headers
                )

                if response.status_code == 204:
                    return {"success": True, "message": "Successfully signed out"}
                error_data = (
                    response.json()
                    if response.content
                    else {"message": "Unknown error during sign out"}
                )
                error_msg = error_data.get("message", "Error during sign out")
                logger.error(f"Sign out error: {error_msg}")
                return {"success": False, "error": error_msg}

        except Exception as e:
            logger.error(f"Exception during sign out: {str(e)}")
            return {
                "success": False,
                "error": "Service unavailable. Please try again later.",
            }

    async def reset_password_request(self, email: EmailStr) -> dict[str, Any]:
        """Send a password reset link to the user's email address."""
        url = f"{self.supabase_url}/auth/v1/recover"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, json={"email": email}, headers=self.headers
                )

                if response.status_code == 200:
                    return {
                        "success": True,
                        "message": "Password reset link sent to your email",
                    }
                error_data = response.json()
                error_msg = error_data.get(
                    "message", "Error sending password reset link"
                )
                logger.error(f"Reset password request error: {error_msg}")
                return {"success": False, "error": error_msg}

        except Exception as e:
            logger.error(f"Exception during reset password request: {str(e)}")
            return {
                "success": False,
                "error": "Service unavailable. Please try again later.",
            }

    async def change_password(self, token: str, password: str) -> dict[str, Any]:
        """Change a user's password using a reset token."""
        url = f"{self.supabase_url}/auth/v1/recover"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    url,
                    json={"token": token, "password": password},
                    headers=self.headers,
                )

                if response.status_code == 200:
                    return {"success": True, "message": "Password changed successfully"}
                error_data = response.json()
                error_msg = error_data.get("message", "Error changing password")
                logger.error(f"Change password error: {error_msg}")
                return {"success": False, "error": error_msg}

        except Exception as e:
            logger.error(f"Exception during change password: {str(e)}")
            return {
                "success": False,
                "error": "Service unavailable. Please try again later.",
            }

    async def verify_email(self, token: str) -> dict[str, Any]:
        """Verify a user's email address using the token sent to their email."""
        url = f"{self.supabase_url}/auth/v1/verify"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, json={"token": token, "type": "signup"}, headers=self.headers
                )

                if response.status_code == 200:
                    return {"success": True, "message": "Email verified successfully"}
                error_data = response.json()
                error_msg = error_data.get("message", "Error verifying email")
                logger.error(f"Verify email error: {error_msg}")
                return {"success": False, "error": error_msg}

        except Exception as e:
            logger.error(f"Exception during email verification: {str(e)}")
            return {
                "success": False,
                "error": "Service unavailable. Please try again later.",
            }

    async def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """Refresh the authentication tokens using the refresh token."""
        url = f"{self.supabase_url}/auth/v1/token?grant_type=refresh_token"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, json={"refresh_token": refresh_token}, headers=self.headers
                )

                if response.status_code == 200:
                    auth_data = response.json()
                    return {
                        "success": True,
                        "session": {
                            "access_token": auth_data.get("access_token"),
                            "refresh_token": auth_data.get("refresh_token"),
                            "expires_at": auth_data.get("expires_at"),
                        },
                    }
                error_data = response.json()
                error_msg = error_data.get("message", "Error refreshing token")
                logger.error(f"Refresh token error: {error_msg}")
                return {"success": False, "error": error_msg}

        except Exception as e:
            logger.error(f"Exception during token refresh: {str(e)}")
            return {
                "success": False,
                "error": "Service unavailable. Please try again later.",
            }

    async def verify_token(self, token: str) -> dict[str, Any]:
        """Verify a token received from the OAuth callback."""
        url = f"{self.supabase_url}/auth/v1/user"

        auth_headers = {**self.headers, "Authorization": f"Bearer {token}"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=auth_headers)

                if response.status_code == 200:
                    user_data = response.json()
                    return {"success": True, "user": user_data}
                error_data = response.json()
                error_msg = error_data.get("message", "Invalid token")
                logger.error(f"Verify token error: {error_msg}")
                return {"success": False, "error": error_msg}

        except Exception as e:
            logger.error(f"Exception during token verification: {str(e)}")
            return {
                "success": False,
                "error": "Service unavailable. Please try again later.",
            }

    async def oauth_initiate(self, provider: str) -> str:
        """Generate the OAuth URL for the specified provider."""
        # Create the redirect URL for the provider
        return f"{self.supabase_url}/auth/v1/authorize?provider={provider}"

    def decode_jwt(self, token: str) -> Optional[dict[str, Any]]:
        """Decode and verify a JWT token."""
        try:
            # Decode the JWT using Supabase's JWT secret
            return jwt.decode(
                token,
                self.supabase_jwt_secret,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
        except jwt.JWTError as e:
            logger.error(f"JWT decode error: {str(e)}")
            return None
