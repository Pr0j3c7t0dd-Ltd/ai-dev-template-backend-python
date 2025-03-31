from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Optional
from src.config.settings import Settings

settings = Settings()

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, token: str) -> bool:
        try:
            payload = decode_jwt(token)
            return bool(payload)
        except JWTError:
            return False

def decode_jwt(token: str) -> Optional[dict]:
    try:
        # Decode the JWT using Supabase's JWT secret
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False}  # Supabase tokens don't include aud claim by default
        )
        return payload
    except JWTError:
        return None

def get_current_user(token: str = Depends(JWTBearer())) -> dict:
    payload = decode_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload 