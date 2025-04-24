from typing import Optional

from src.models import UserSettings, UserSettingsBase
from src.repositories.base import BaseRepository
from src.utils.logger import logger


class UserSettingsRepository(BaseRepository):
    """Repository for User Settings."""

    def __init__(self, auth_token: Optional[str] = None):
        """Initialize the UserSettings repository with an optional auth token."""
        self.table_name = "user_settings"
        super().__init__(auth_token=auth_token)

    def get_user_settings(self, user_id: str) -> UserSettings:
        """
        Get user settings for a user.

        This method first ensures the user settings exist by calling the
        ensure_user_settings RPC, then fetches the settings from the database.

        Args:
            user_id: The user's ID

        Returns:
            UserSettings object with the user's settings

        Raises:
            Exception: If there's an error retrieving the settings
        """
        try:
            # First ensure settings exist for this user
            logger.debug(f"Ensuring user settings exist for user_id: {user_id}")
            self._ensure_user_settings(user_id)

            # Then fetch the settings
            logger.debug(f"Fetching settings for user_id: {user_id}")
            result = self.table.select("*").eq("id", user_id).execute()

            if not result.data:
                logger.warning(f"No settings found for user_id: {user_id}")
                error_msg = f"Settings not found for user: {user_id}"
                raise ValueError(error_msg)

            # Convert to model
            settings_data = result.data[0]
            logger.debug(f"Retrieved settings: {settings_data}")

            return UserSettings(
                id=settings_data["id"],
                theme=settings_data["theme"],
                language=settings_data["language"],
                timezone=settings_data["timezone"],
                created_at=settings_data["created_at"],
                updated_at=settings_data["updated_at"],
            )

        except Exception as e:
            logger.error(f"Error getting user settings: {str(e)}")
            raise

    def update_user_settings(
        self, user_id: str, settings: UserSettingsBase
    ) -> UserSettings:
        """
        Update user settings for a user.

        This method first ensures the user settings exist by calling the
        ensure_user_settings RPC, then updates the settings in the database.

        Args:
            user_id: The user's ID
            settings: UserSettingsBase object with the new settings

        Returns:
            UserSettings object with the updated settings

        Raises:
            Exception: If there's an error updating the settings
        """
        try:
            # First ensure settings exist for this user
            logger.debug(f"Ensuring user settings exist for user_id: {user_id}")
            self._ensure_user_settings(user_id)

            # Then update the settings
            logger.debug(
                f"Updating settings for user_id: {user_id} with data: {settings.model_dump()}"
            )
            result = (
                self.table.update(settings.model_dump()).eq("id", user_id).execute()
            )

            if not result.data:
                logger.warning(f"No settings updated for user_id: {user_id}")
                error_msg = f"Settings not found for user: {user_id}"
                raise ValueError(error_msg)

            # Convert to model
            settings_data = result.data[0]
            logger.debug(f"Updated settings: {settings_data}")

            return UserSettings(
                id=settings_data["id"],
                theme=settings_data["theme"],
                language=settings_data["language"],
                timezone=settings_data["timezone"],
                created_at=settings_data["created_at"],
                updated_at=settings_data["updated_at"],
            )

        except Exception as e:
            logger.error(f"Error updating user settings: {str(e)}")
            raise

    def _ensure_user_settings(self, user_id: str) -> dict:
        """
        Ensure user settings exist by calling the ensure_user_settings RPC.

        Args:
            user_id: The user's ID

        Returns:
            dict with the RPC response

        Raises:
            Exception: If there's an error calling the RPC
        """
        try:
            logger.debug(f"Calling ensure_user_settings RPC for user_id: {user_id}")

            # First, check if the user exists in auth.users table
            # Use the rpc method instead of direct table access to handle schema correctly
            user_check = self._supabase_client.rpc(
                "check_user_exists", {"user_id_param": user_id}
            ).execute()

            if not user_check.data or not user_check.data.get("exists", False):
                logger.error(
                    f"Cannot ensure settings: User with ID {user_id} does not exist in auth.users table"
                )
                error_msg = f"User with ID {user_id} does not exist. Valid user account required."
                raise ValueError(error_msg)

            # If user exists, proceed with ensuring settings
            response = self._supabase_client.rpc("ensure_user_settings").execute()

            if not response.data:
                logger.warning("No response data from ensure_user_settings RPC")
                error_msg = "Failed to ensure user settings"
                raise ValueError(error_msg)

            logger.debug(f"ensure_user_settings RPC response: {response.data}")
            return response.data

        except ValueError as e:
            # Re-raise ValueError for known issues like missing user
            logger.error(f"Error ensuring user settings: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error ensuring user settings: {str(e)}")
            raise
