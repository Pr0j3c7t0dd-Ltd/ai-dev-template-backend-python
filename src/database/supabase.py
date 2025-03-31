from functools import lru_cache

from src.config.settings import get_settings
from supabase import create_client


@lru_cache
async def get_supabase_client():
    """
    Creates and returns a cached Supabase client instance.
    Uses environment variables for configuration.
    """
    settings = get_settings()
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
