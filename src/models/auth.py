"""Authentication models."""

from typing import Any, Optional

from pydantic import BaseModel, EmailStr, field_validator


class SignUpRequest(BaseModel):
    """Request model for sign up endpoint."""

    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Validate password complexity."""
        if len(v) < 8:
            error_msg = "Password must be at least 8 characters long"
            raise ValueError(error_msg)
        if not any(c.isupper() for c in v):
            error_msg = "Password must contain at least one uppercase letter"
            raise ValueError(error_msg)
        if not any(c.islower() for c in v):
            error_msg = "Password must contain at least one lowercase letter"
            raise ValueError(error_msg)
        if not any(c.isdigit() for c in v):
            error_msg = "Password must contain at least one number"
            raise ValueError(error_msg)
        if not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?/~" for c in v):
            error_msg = "Password must contain at least one special character"
            raise ValueError(error_msg)
        return v


class SignInRequest(BaseModel):
    """Request model for sign in endpoint."""

    email: EmailStr
    password: str


class ResetPasswordRequest(BaseModel):
    """Request model for reset password endpoint."""

    email: EmailStr


class ChangePasswordRequest(BaseModel):
    """Request model for change password endpoint."""

    token: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Validate password complexity."""
        if len(v) < 8:
            error_msg = "Password must be at least 8 characters long"
            raise ValueError(error_msg)
        if not any(c.isupper() for c in v):
            error_msg = "Password must contain at least one uppercase letter"
            raise ValueError(error_msg)
        if not any(c.islower() for c in v):
            error_msg = "Password must contain at least one lowercase letter"
            raise ValueError(error_msg)
        if not any(c.isdigit() for c in v):
            error_msg = "Password must contain at least one number"
            raise ValueError(error_msg)
        if not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?/~" for c in v):
            error_msg = "Password must contain at least one special character"
            raise ValueError(error_msg)
        return v


class RefreshTokenRequest(BaseModel):
    """Request model for refresh token endpoint."""

    refresh_token: str


class VerifyTokenRequest(BaseModel):
    """Request model for verify token endpoint."""

    token: str


class UserResponse(BaseModel):
    """User data returned in authentication responses."""

    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    email_verified: bool = False


class SessionResponse(BaseModel):
    """Session data returned in authentication responses."""

    access_token: str
    refresh_token: str
    expires_at: int


class SignUpResponse(BaseModel):
    """Response model for sign up endpoint."""

    success: bool
    message: Optional[str] = None
    error: Optional[str] = None


class SignInResponse(BaseModel):
    """Response model for sign in endpoint."""

    success: bool
    user: Optional[UserResponse] = None
    session: Optional[SessionResponse] = None
    error: Optional[str] = None


class SignOutResponse(BaseModel):
    """Response model for sign out endpoint."""

    success: bool
    message: Optional[str] = None
    error: Optional[str] = None


class ResetPasswordResponse(BaseModel):
    """Response model for reset password endpoint."""

    success: bool
    message: Optional[str] = None
    error: Optional[str] = None


class ChangePasswordResponse(BaseModel):
    """Response model for change password endpoint."""

    success: bool
    message: Optional[str] = None
    error: Optional[str] = None


class RefreshTokenResponse(BaseModel):
    """Response model for refresh token endpoint."""

    success: bool
    session: Optional[SessionResponse] = None
    error: Optional[str] = None


class VerifyTokenResponse(BaseModel):
    """Response model for verify token endpoint."""

    success: bool
    user: Optional[dict[str, Any]] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str
    details: dict[str, str]
    timestamp: str
    version: str
