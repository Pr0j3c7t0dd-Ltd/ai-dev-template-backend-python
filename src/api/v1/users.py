from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.models import UserResponse, UserSettings, UserSettingsBase
from src.repositories.user_settings import UserSettingsRepository
from src.utils.auth import conditional_auth
from src.utils.logger import logger

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(request: Request, user=Depends(conditional_auth)):
    """Get the current user's information from their JWT token."""
    logger.debug(f"Processing /me endpoint - Method: {request.method}")

    # For OPTIONS requests, the conditional_auth middleware already handles it by returning None
    if request.method == "OPTIONS":
        logger.debug("OPTIONS request to /me - returning empty response")
        return {}

    # For regular requests, ensure we have valid user data
    if not user or "sub" not in user:
        logger.warning("Missing or invalid user data in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    logger.debug(f"Returning user info for user_id: {user.get('sub')}")
    return {
        "id": user.get("sub"),
        "email": user.get("email"),
        "first_name": user.get("user_metadata", {}).get("first_name"),
        "last_name": user.get("user_metadata", {}).get("last_name"),
        "avatar_url": user.get("user_metadata", {}).get("avatar_url"),
        "created_at": user.get("created_at"),
        "updated_at": user.get("updated_at"),
        "email_verified": user.get("email_confirmed_at") is not None,
    }


@router.get("/me/settings", response_model=UserSettings)
async def get_user_settings(request: Request, user=Depends(conditional_auth)):
    """Get the current user's settings."""
    logger.debug(f"Processing /me/settings endpoint - Method: {request.method}")

    # For OPTIONS requests, return empty response
    if request.method == "OPTIONS":
        logger.debug("OPTIONS request to /me/settings - returning empty response")
        return {}

    # Ensure we have valid user data
    if not user or "sub" not in user:
        logger.warning("Missing or invalid user data in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    user_id = user.get("sub")
    logger.debug(f"Fetching settings for user_id: {user_id}")

    # Get the auth token from the request
    auth_header = request.headers.get("Authorization")
    auth_token = None
    if auth_header and auth_header.startswith("Bearer "):
        auth_token = auth_header.replace("Bearer ", "")
        logger.debug("Found auth token in request")

    # Get user settings from repository
    try:
        # Add debug logging
        logger.debug("Creating UserSettingsRepository instance")
        repo = UserSettingsRepository(auth_token=auth_token)

        # Log each step
        logger.debug(f"Calling get_user_settings with user_id: {user_id}")
        result = repo.get_user_settings(user_id)

        logger.debug(f"Successfully retrieved user settings: {result}")
        return result
    except ValueError as e:
        # Handle specific validation errors more precisely
        error_message = str(e)
        if "does not exist" in error_message:
            logger.error(f"User account issue: {error_message}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User account issue: {error_message}",
            ) from e
        logger.error(f"Error fetching user settings: {error_message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error fetching user settings: {error_message}",
        ) from e
    except Exception as e:
        logger.error(f"Error fetching user settings: {str(e)}", exc_info=True)
        # Check for foreign key violation error
        error_str = str(e)
        if (
            "violates foreign key constraint" in error_str
            and "user_settings_id_fkey" in error_str
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account mismatch. Please sign out and sign in again.",
            ) from e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching user settings",
        ) from e


@router.put("/me/settings", response_model=UserSettings)
async def update_user_settings(
    settings: UserSettingsBase, request: Request, user=Depends(conditional_auth)
):
    """Update the current user's settings."""
    logger.debug(f"Processing /me/settings update endpoint - Method: {request.method}")

    # Ensure we have valid user data
    if not user or "sub" not in user:
        logger.warning("Missing or invalid user data in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    user_id = user.get("sub")
    logger.debug(f"Updating settings for user_id: {user_id} with data: {settings}")

    # Get the auth token from the request
    auth_header = request.headers.get("Authorization")
    auth_token = None
    if auth_header and auth_header.startswith("Bearer "):
        auth_token = auth_header.replace("Bearer ", "")
        logger.debug("Found auth token in request")

    # Update user settings in repository
    try:
        repo = UserSettingsRepository(auth_token=auth_token)
        return repo.update_user_settings(user_id, settings)
    except ValueError as e:
        # Handle specific validation errors more precisely
        error_message = str(e)
        if "does not exist" in error_message:
            logger.error(f"User account issue: {error_message}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User account issue: {error_message}",
            ) from e
        logger.error(f"Error updating user settings: {error_message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating user settings: {error_message}",
        ) from e
    except Exception as e:
        logger.error(f"Error updating user settings: {str(e)}")
        # Check for foreign key violation error
        error_str = str(e)
        if (
            "violates foreign key constraint" in error_str
            and "user_settings_id_fkey" in error_str
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account mismatch. Please sign out and sign in again.",
            ) from e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user settings",
        ) from e
