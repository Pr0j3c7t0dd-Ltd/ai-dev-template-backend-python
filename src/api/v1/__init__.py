from fastapi import APIRouter, Depends

from src.config.settings import Settings
from src.utils.auth import JWTBearer

from . import health, users

settings = Settings()

# Create the main router
router = APIRouter(prefix=settings.API_V1_STR)

# Add global JWT authentication to all routes except /health
router.include_router(
    health.router,
    dependencies=[],  # No authentication for health check
)

# Add protected routes
router.include_router(
    users.router,
    dependencies=[Depends(JWTBearer())],  # Protected by JWT
)
