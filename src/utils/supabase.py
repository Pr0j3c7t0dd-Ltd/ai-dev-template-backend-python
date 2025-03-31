from supabase import create_client, Client
from src.config.settings import Settings

settings = Settings()

def get_supabase_client() -> Client:
    """Get a configured Supabase client instance."""
    return create_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=settings.SUPABASE_KEY
    ) 