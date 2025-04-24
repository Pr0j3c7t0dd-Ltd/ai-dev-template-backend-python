"""
Base class for repositories.
"""

from src.database.supabase import get_supabase_client
from src.utils.logger import logger


class BaseRepository:
    """
    Base class for repositories.
    """

    table_name: str = ""

    def __init__(self, auth_token: str = None):
        """
        Initialize a new repository instance.

        Args:
            auth_token: Optional JWT token for authenticated requests
        """
        self._supabase_client = None
        self._auth_token = auth_token
        self.initialize()

    def initialize(self):
        """
        Initialize the repository with a Supabase client.
        """
        logger.debug("Initializing Supabase client in BaseRepository")
        try:
            self._supabase_client = get_supabase_client(self._auth_token)
            logger.debug("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Supabase client: {str(e)}")
            error_message = f"Failed to initialize Supabase client: {str(e)}"
            raise Exception(error_message) from e

    @property
    def table(self):
        """
        Get the table for this repository.
        """
        if not self.table_name:
            logger.error("table_name is not set")
            error_message = "table_name is not set"
            raise ValueError(error_message)

        if not self._supabase_client:
            logger.error("Supabase client is not initialized")
            error_message = "Supabase client is not initialized"
            raise ValueError(error_message)

        return self._supabase_client.table(self.table_name)
