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

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={"email": email, "password": password},
                    headers=self.headers,
                )

                if response.status_code == 200:
                    return {
                        "success": True,
                        "message": "Account created successfully. Please check your email to confirm your account.",
                    }
                error_data = response.json()
                error_msg = error_data.get("message", "Unknown error during signup")
                logger.error(f"Signup error: {error_msg}")
                return {"success": False, "error": error_msg}

        except Exception as e:
            logger.error(f"Exception during signup: {str(e)}")
            return {
                "success": False,
                "error": "Service unavailable. Please try again later.",
            }

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
