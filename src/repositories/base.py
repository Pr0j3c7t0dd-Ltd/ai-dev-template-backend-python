from src.database.supabase import get_supabase_client


class BaseRepository:
    """Base repository class with Supabase client integration."""

    def __init__(self):
        self.supabase = None
        self.table_name: str = ""  # Override in child classes

    async def initialize(self):
        """Initialize the Supabase client asynchronously."""
        if self.supabase is None:
            self.supabase = await get_supabase_client()
        return self

    @property
    def table(self):
        """Returns the Supabase table reference."""
        if not self.table_name:
            error_message = "table_name must be set in child class"
            raise ValueError(error_message)
        if self.supabase is None:
            error_message = "Supabase client not initialized. Call initialize() first."
            raise ValueError(error_message)
        return self.supabase.table(self.table_name)
