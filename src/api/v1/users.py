from fastapi import APIRouter, Depends

from src.utils.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_current_user_info(user: dict = Depends(get_current_user)):
    """Get the current user's information from their JWT token."""
    return {
        "id": user.get("sub"),
        "email": user.get("email"),
        "role": user.get("role", "user"),
        "aud": user.get("aud"),
        "exp": user.get("exp"),
    }
