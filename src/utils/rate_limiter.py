"""Rate limiting utility for the application."""

import os

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def get_key_func(request):
    """Get a key function that works in both normal and test environments."""
    # In a test environment, use a fixed IP to avoid errors
    if os.environ.get("TESTING", "").lower() == "true":
        return "test-client"

    # Handle TestClient requests in pytest
    if not isinstance(request, Request):
        return "test-client"

    # In normal operation, use the real remote address
    return get_remote_address(request)


# Create a single limiter instance for the application
limiter = Limiter(key_func=get_key_func)
