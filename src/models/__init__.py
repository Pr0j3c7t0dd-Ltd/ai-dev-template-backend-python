"""Data models for the application."""

from typing import Optional

from pydantic import UUID4, BaseModel, Field

# Import all auth models
from .auth import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    HealthResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    SessionResponse,
    SignInRequest,
    SignInResponse,
    SignOutResponse,
    SignUpRequest,
    SignUpResponse,
    UserResponse,
    VerifyTokenRequest,
    VerifyTokenResponse,
)


class UserSettingsBase(BaseModel):
    theme: Optional[str] = "light"
    language: Optional[str] = "en"
    timezone: Optional[str] = "UTC"


class UserSettings(UserSettingsBase):
    id: UUID4
