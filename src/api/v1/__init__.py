from fastapi import APIRouter, Depends

from src.config.settings import Settings
from src.utils.auth import JWTBearer, conditional_auth, get_current_user
from src.utils.logger import logger

from . import auth, health, users

settings = Settings()

# Create the main router
router = APIRouter(prefix=settings.API_V1_STR)

# Add auth routes without authentication dependencies
router.include_router(
    auth.router,
    dependencies=[],  # No authentication for auth endpoints
)

# Add global JWT authentication to all routes except /health
router.include_router(
    health.router,
    dependencies=[],  # No authentication for health check
)

# Add protected routes with conditional authentication
router.include_router(
    users.router,
    dependencies=[Depends(conditional_auth)],
    # Ensure OPTIONS requests don't trigger 400 errors
    responses={204: {"description": "No content for preflight OPTIONS requests"}},
)
