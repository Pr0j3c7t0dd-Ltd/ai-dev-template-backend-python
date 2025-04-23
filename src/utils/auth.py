from typing import Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from jose import JWTError, jwt

from src.config.settings import Settings
from src.repositories.user_settings import UserSettingsRepository
from src.utils.logger import logger

settings = Settings()

# OAuth2PasswordBearer for Swagger UI authentication
# This is only used for Swagger UI documentation - not for actual authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="", auto_error=False)


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        logger.debug(
            f"JWTBearer processing request to {request.url.path} [{request.method}]"
        )
        try:
            credentials: HTTPAuthorizationCredentials = await super().__call__(request)
            if credentials:
                if credentials.scheme != "Bearer":
                    logger.warning(
                        f"Invalid authentication scheme: {credentials.scheme}"
                    )
                    raise HTTPException(
                        status_code=403, detail="Invalid authentication scheme."
                    )
                if not self.verify_jwt(credentials.credentials):
                    logger.warning("Invalid token or expired token")
                    raise HTTPException(
                        status_code=403, detail="Invalid token or expired token."
                    )
                return credentials.credentials
            logger.warning("Invalid authorization code")
            raise HTTPException(status_code=403, detail="Invalid authorization code.")
        except HTTPException as e:
            logger.debug(f"Authentication error: {e.status_code} - {e.detail}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in JWTBearer: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error") from e

    def verify_jwt(self, token: str) -> bool:
        try:
            payload = decode_jwt(token)
            return bool(payload)
        except JWTError:
            return False


def decode_jwt(token: str) -> Optional[dict]:
    try:
        # Decode the JWT using Supabase's JWT secret
        return jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={
                "verify_aud": False
            },  # Supabase tokens don't include aud claim by default
        )
    except JWTError:
        return None


async def get_current_user(token: str = Depends(JWTBearer())) -> dict:
    payload = decode_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Ensure user settings exist
    user_id = payload.get("sub")
    if user_id:
        user_settings_repo = UserSettingsRepository()
        try:
            # Ensure user settings exist - this calls our database function
            user_settings_repo.ensure_user_settings(user_id)
        except Exception as e:
            # Log the error but don't block the request
            logger.error(f"Error ensuring user settings: {str(e)}")
            # Continue without raising an exception - this allows the request to proceed
            # even if the user settings creation fails

    return payload


# For Swagger UI usage - accepts token from various sources
async def get_current_user_for_swagger(
    http_bearer_token: str = Depends(JWTBearer(auto_error=False)),
    oauth2_token: str = Depends(oauth2_scheme),
) -> dict:
    """Get current user for Swagger UI.

    This function accepts tokens from multiple sources to support Swagger UI.
    """
    token = http_bearer_token or oauth2_token
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Ensure user settings exist
    user_id = payload.get("sub")
    if user_id:
        user_settings_repo = UserSettingsRepository()
        try:
            # Ensure user settings exist
            user_settings_repo.ensure_user_settings(user_id)
        except Exception as e:
            # Log the error but don't block the request
            print(f"Error ensuring user settings: {str(e)}")

    return payload


async def conditional_auth(request: Request):
    """Skip authentication for OPTIONS requests to handle CORS preflight properly."""
    if request.method == "OPTIONS":
        logger.debug("Skipping authentication for OPTIONS request")
        return None  # Return None instead of empty dict for OPTIONS

    # For non-OPTIONS requests, use the regular JWT authentication
    try:
        jwt_bearer = JWTBearer()
        token = await jwt_bearer(request)
        return await get_current_user(token)
    except HTTPException as e:
        logger.warning(f"Authentication failed: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in conditional_auth: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e
