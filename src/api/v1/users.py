from fastapi import APIRouter, Depends, Request

from src.utils.auth import conditional_auth
from src.utils.logger import logger

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
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
        return {"error": "Unauthorized"}

    logger.debug(f"Returning user info for user_id: {user.get('sub')}")
    return {
        "id": user.get("sub"),
        "email": user.get("email"),
        "role": user.get("role", "user"),
        "aud": user.get("aud"),
        "exp": user.get("exp"),
    }
