from src.repositories.base import BaseRepository


class UserSettingsRepository(BaseRepository):
    """Repository for interacting with user_settings table."""

    def __init__(self):
        super().__init__()
        self.table_name = "user_settings"

    async def ensure_user_settings(self, user_id: str) -> dict:
        """
        Ensures that a user_settings record exists for the given user ID.
        If it doesn't exist, creates one with default values.

        Args:
            user_id: The UUID of the user

        Returns:
            The user settings record
        """
        # Initialize the client if not already initialized
        await self.initialize()

        # Call the Supabase RPC function we created
        try:
            result = await self.supabase.rpc("ensure_user_settings").execute()

            # Fetch the user settings after ensuring it exists
            settings = await self.table.select("*").eq("id", user_id).single().execute()
            return settings.data
        except Exception:
            # If the RPC fails, try direct insert
            try:
                # Check if the user settings already exist
                existing = await self.table.select("*").eq("id", user_id).execute()
                if existing.data:
                    return existing.data[0]

                # Create default user settings
                result = await self.table.insert({"id": user_id}).execute()
                return result.data[0] if result.data else {}
            except Exception as inner_e:
                error_message = f"Failed to ensure user settings: {str(inner_e)}"
                raise Exception(error_message) from inner_e
