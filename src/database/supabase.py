from functools import lru_cache

from src.config.settings import get_settings
from src.utils.logger import logger
from supabase import create_client


@lru_cache
def get_supabase_client():
    """
    Creates and returns a cached Supabase client instance.
    Uses environment variables for configuration.
    """
    logger.debug("Creating Supabase client")
    settings = get_settings()
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    logger.debug("Supabase client created successfully")
    return client
