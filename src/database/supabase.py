from functools import lru_cache

from supabase import Client, create_client

from src.config.settings import get_settings


@lru_cache
def get_supabase_client() -> Client:
    """
    Creates and returns a cached Supabase client instance.
    Uses environment variables for configuration.
    """
    settings = get_settings()
    return create_client(
        supabase_url=settings.SUPABASE_URL, supabase_key=settings.SUPABASE_KEY
    )
