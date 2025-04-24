from typing import Optional

from src.config.settings import get_settings
from src.utils.logger import logger
from supabase import create_client


def get_supabase_client(auth_token: Optional[str] = None):
    """
    Creates and returns a Supabase client instance.
    Uses environment variables for configuration.

    Args:
        auth_token: Optional JWT token for authenticated requests

    Returns:
        A Supabase client instance
    """
    logger.debug("Creating Supabase client")
    settings = get_settings()

    # Only use SUPABASE_ANON_KEY (no fallback to legacy key)
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

    # Set auth token if provided
    if auth_token:
        logger.debug("Setting auth token on Supabase client")
        # Just set the auth header directly
        client.postgrest.auth(auth_token)

    logger.debug("Supabase client created successfully")
    return client
