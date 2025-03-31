from supabase import Client

from src.database.supabase import get_supabase_client


class BaseRepository:
    """Base repository class with Supabase client integration."""

    def __init__(self):
        self.supabase: Client = get_supabase_client()
        self.table_name: str = ""  # Override in child classes

    @property
    def table(self):
        """Returns the Supabase table reference."""
        if not self.table_name:
            error_message = "table_name must be set in child class"
            raise ValueError(error_message)
        return self.supabase.table(self.table_name)
