from src.models import UserSettingsBase
from src.repositories.base import BaseRepository
from src.utils.logger import logger


class UserSettingsRepository(BaseRepository):
    """Repository for interacting with user_settings table."""

    def __init__(self):
        self.table_name = "user_settings"
        super().__init__()

    def ensure_user_settings(self, user_id: str) -> dict:
        """
        Ensures that a user_settings record exists for the given user ID.
        If it doesn't exist, creates one with default values.

        Args:
            user_id: The UUID of the user

        Returns:
            The user settings record
        """
        try:
            # Check if the user settings already exist
            logger.debug(f"Checking if user settings exist for user_id: {user_id}")
            existing = self.table.select("*").eq("id", user_id).execute()

            # Log the result
            logger.debug(
                f"Existing user settings query result: {existing.__dict__ if hasattr(existing, '__dict__') else existing}"
            )

            if hasattr(existing, "data") and existing.data:
                logger.debug(f"Found existing settings: {existing.data}")
                return existing.data[0]

            # Create default user settings - this is better than calling an RPC function
            logger.debug(
                f"No settings found, creating default settings for user_id: {user_id}"
            )
            result = self.table.insert({"id": user_id}).execute()

            # Log the result
            logger.debug(
                f"Insert result: {result.__dict__ if hasattr(result, '__dict__') else result}"
            )

            if hasattr(result, "data") and result.data:
                logger.debug(f"Successfully created user settings: {result.data[0]}")
                return result.data[0]
            logger.warning("No data returned from insert operation")
            return {}
        except Exception as e:
            logger.error(f"Failed to ensure user settings: {str(e)}", exc_info=True)
            error_message = f"Failed to ensure user settings: {str(e)}"
            raise Exception(error_message) from e

    def get_user_settings(self, user_id: str) -> dict:
        """
        Get the user settings for a specific user.

        Args:
            user_id: The UUID of the user

        Returns:
            The user settings record
        """
        # Ensure the user settings exist
        logger.debug(f"Ensuring user settings exist for user_id: {user_id}")
        self.ensure_user_settings(user_id)

        # Get the settings
        logger.debug(f"Fetching user settings for user_id: {user_id}")
        try:
            result = self.table.select("*").eq("id", user_id).single().execute()
            logger.debug(
                f"User settings query result: {result.__dict__ if hasattr(result, '__dict__') else result}"
            )

            if hasattr(result, "data"):
                logger.debug(f"User settings data: {result.data}")
                return result.data
            logger.warning("No data returned from select operation")
            return {}
        except Exception as e:
            logger.error(f"Error fetching user settings: {str(e)}", exc_info=True)
            error_message = f"Error fetching user settings: {str(e)}"
            raise Exception(error_message) from e

    def update_user_settings(self, user_id: str, settings: UserSettingsBase) -> dict:
        """
        Update the user settings for a specific user.

        Args:
            user_id: The UUID of the user
            settings: The settings to update

        Returns:
            The updated user settings record
        """
        # Ensure the user settings exist
        self.ensure_user_settings(user_id)

        # Update the settings
        result = (
            self.table.update(settings.model_dump(exclude_unset=True))
            .eq("id", user_id)
            .execute()
        )
        return result.data[0] if result.data else {}
