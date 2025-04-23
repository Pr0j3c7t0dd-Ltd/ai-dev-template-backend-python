"""Authentication endpoints."""

import os

from fastapi import APIRouter, Request, Response, status
from fastapi.responses import JSONResponse, RedirectResponse

from src.config.settings import get_settings
from src.models import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    RefreshTokenResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    SignInRequest,
    SignInResponse,
    SignOutResponse,
    SignUpRequest,
    SignUpResponse,
    VerifyTokenRequest,
    VerifyTokenResponse,
)
from src.services.auth_service import AuthService
from src.utils.logger import logger
from src.utils.rate_limiter import limiter

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()

# Cookie settings
ACCESS_TOKEN_EXPIRES_IN_SECONDS = 15 * 60  # 15 minutes
REFRESH_TOKEN_EXPIRES_IN_SECONDS = 7 * 24 * 60 * 60  # 7 days
SECURE_COOKIES = settings.ENVIRONMENT.lower() != "development"

# Check if we're in a test environment to conditionally apply rate limiting
IS_TESTING = os.environ.get("TESTING", "").lower() == "true"


# Function to conditionally apply rate limiting decorator
def apply_rate_limit(func):
    """Apply rate limiting only in non-test environments."""
    if IS_TESTING:
        return func
    return limiter.limit("5/minute")(func)


@router.post("/sign-up", response_model=SignUpResponse)
async def sign_up(request: SignUpRequest, _req: Request) -> SignUpResponse:
    """Register a new user with email and password."""
    logger.debug(f"Sign-up request received for email: {request.email}")

    # Call auth service
    result = await auth_service.sign_up(request.email, request.password)

    # If signup failed, log additional details and return enhanced error information
    if not result["success"]:
        error_msg = result.get("error", "Unknown error")
        error_code = result.get("error_code", "unknown_error")
        details = result.get("details", {})

        logger.error(
            f"Sign-up failed for {request.email}: {error_msg} (code: {error_code})"
        )

        # Return all error details to the frontend
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": error_msg,
                "error_code": error_code,
                "details": details,
            },
        )

    logger.info(f"Sign-up successful for email: {request.email}")
    return result


@router.post("/sign-in", response_model=SignInResponse)
async def sign_in(
    request: SignInRequest, response: Response, _req: Request
) -> SignInResponse:
    """Authenticate a user with email and password."""
    result = await auth_service.sign_in(request.email, request.password)

    if result["success"]:
        # Set HTTP-only cookies
        access_token = result["session"]["access_token"]
        refresh_token = result["session"]["refresh_token"]

        # Set the access token cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=SECURE_COOKIES,
            max_age=ACCESS_TOKEN_EXPIRES_IN_SECONDS,
            samesite="lax",
        )

        # Set the refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=SECURE_COOKIES,
            max_age=REFRESH_TOKEN_EXPIRES_IN_SECONDS,
            samesite="lax",
        )

        return result
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=result)


@router.post("/sign-out", response_model=SignOutResponse)
async def sign_out(request: Request, response: Response) -> SignOutResponse:
    """Sign out the current user by invalidating tokens and clearing cookies."""
    # Get the refresh token from cookies
    refresh_token = request.cookies.get("refresh_token")

    # Invalidate the token with Supabase if it exists
    if refresh_token:
        await auth_service.sign_out(refresh_token)

    # Clear cookies regardless of the result
    response.delete_cookie(
        key="access_token", secure=SECURE_COOKIES, httponly=True, samesite="lax"
    )
    response.delete_cookie(
        key="refresh_token", secure=SECURE_COOKIES, httponly=True, samesite="lax"
    )

    return {"success": True, "message": "Successfully signed out"}


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    request: ResetPasswordRequest, _req: Request
) -> ResetPasswordResponse:
    """Send a password reset link to the user's email address."""
    result = await auth_service.reset_password_request(request.email)

    if not result["success"]:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)

    return result


@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(
    request: ChangePasswordRequest, _req: Request
) -> ChangePasswordResponse:
    """Change a user's password using a reset token."""
    result = await auth_service.change_password(request.token, request.password)

    if not result["success"]:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)

    return result


@router.get("/verify-email/{token}")
async def verify_email(token: str):
    """Verify a user's email address using the token sent to their email."""
    result = await auth_service.verify_email(token)

    # Redirect to frontend with success or error message
    frontend_url = (
        settings.CORS_ORIGINS[0] if settings.CORS_ORIGINS else "http://localhost:3000"
    )

    if result["success"]:
        redirect_url = f"{frontend_url}/auth/email-verified?success=true"
    else:
        error = result.get("error", "Failed to verify email")
        redirect_url = f"{frontend_url}/auth/email-verified?success=false&error={error}"

    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(request: Request, response: Response) -> RefreshTokenResponse:
    """Refresh the authentication tokens using the refresh token."""
    # Get the refresh token from cookies
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"success": False, "error": "Refresh token not found"},
        )

    result = await auth_service.refresh_token(refresh_token)

    if result["success"]:
        # Set new HTTP-only cookies
        access_token = result["session"]["access_token"]
        new_refresh_token = result["session"]["refresh_token"]

        # Set the access token cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=SECURE_COOKIES,
            max_age=ACCESS_TOKEN_EXPIRES_IN_SECONDS,
            samesite="lax",
        )

        # Set the refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=SECURE_COOKIES,
            max_age=REFRESH_TOKEN_EXPIRES_IN_SECONDS,
            samesite="lax",
        )

        return result
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=result)


@router.post("/verify-token", response_model=VerifyTokenResponse)
async def verify_token(
    request: VerifyTokenRequest, response: Response, _req: Request
) -> VerifyTokenResponse:
    """Verify a token received from the OAuth callback and set session cookies."""
    result = await auth_service.verify_token(request.token)

    if result["success"] and result.get("user"):
        # Extract user information
        user = result["user"]

        # Set HTTP-only cookies if needed
        if "session" in result:
            access_token = result["session"]["access_token"]
            refresh_token = result["session"]["refresh_token"]

            # Set the access token cookie
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=SECURE_COOKIES,
                max_age=ACCESS_TOKEN_EXPIRES_IN_SECONDS,
                samesite="lax",
            )

            # Set the refresh token cookie
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=SECURE_COOKIES,
                max_age=REFRESH_TOKEN_EXPIRES_IN_SECONDS,
                samesite="lax",
            )

        return {"success": True, "user": user}
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"success": False, "error": result.get("error", "Invalid token")},
    )


@router.get("/oauth/{provider}")
async def oauth_login(provider: str, request: Request):  # noqa: ARG001 - Required by limiter
    """Initiate OAuth authentication flow with the specified provider."""
    redirect_url = await auth_service.oauth_initiate(provider)
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
