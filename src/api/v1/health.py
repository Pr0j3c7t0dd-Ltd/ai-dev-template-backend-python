import datetime

import httpx
from fastapi import APIRouter

from src.config.settings import get_settings
from src.models import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    # Initialize database status
    db_status = "connected"
    services_status = "operational"

    # Check database connection directly using the Supabase health endpoint
    try:
        # Get settings
        settings = get_settings()

        # Make a direct HTTP request to the Supabase health endpoint
        # This avoids authentication issues and doesn't require specific tables
        async with httpx.AsyncClient() as client:
            url = f"{settings.SUPABASE_URL}/rest/v1/"
            headers = {
                "apikey": settings.SUPABASE_KEY,
                "Content-Type": "application/json",
            }
            response = await client.get(url, headers=headers)
            response.raise_for_status()  # Raises an exception for 4XX/5XX responses

        # If we get here, the connection is working
    except Exception:
        db_status = "error"

    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "details": {"database": db_status, "services": services_status},
        "timestamp": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
        "version": "1.0.0",
    }
