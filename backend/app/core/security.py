"""Authentication and security helpers for Supabase Auth JWT validation."""

from typing import Any, Dict, Optional
import jwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr

from app.core.config import settings
from app.core.exceptions import AuthenticationError

security_scheme = HTTPBearer(auto_error=False)


class AuthenticatedUser(BaseModel):
    """Authenticated user context extracted from validated Supabase Auth token."""

    id: str
    email: Optional[str] = None
    role: str = "authenticated"
    user_metadata: Dict[str, Any] = {}


def decode_supabase_jwt(token: str) -> AuthenticatedUser:
    """Validate and decode a Supabase Auth JWT token."""
    try:
        # Supabase signs user access tokens with HMAC-SHA256 using SUPABASE_JWT_SECRET
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_exp": True, "verify_aud": False},
        )
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationError("Authentication token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthenticationError("Invalid authentication token") from exc

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Token missing user subject identifier")

    return AuthenticatedUser(
        id=user_id,
        email=payload.get("email"),
        role=payload.get("role", "authenticated"),
        user_metadata=payload.get("user_metadata", {}),
    )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> AuthenticatedUser:
    """FastAPI dependency to extract and validate the authenticated user from Bearer token."""
    if not credentials or not credentials.credentials:
        raise AuthenticationError("Missing Bearer authorization header")

    token = credentials.credentials
    # First attempt fast local verification (HS256 legacy secret)
    try:
        return decode_supabase_jwt(token)
    except AuthenticationError as err:
        if "expired" in str(err.message).lower():
            raise
        # Fallback to Supabase Auth client for asymmetric ECC (P-256) tokens
        try:
            from app.integrations.supabase_client import SupabaseAuthClient
            auth_client = SupabaseAuthClient()
            user_data = await auth_client.get_user_by_token(token)
            return AuthenticatedUser(
                id=user_data["id"],
                email=user_data.get("email"),
                role="authenticated",
                user_metadata=user_data.get("user_metadata", {}),
            )
        except Exception:
            raise err


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> Optional[AuthenticatedUser]:
    """FastAPI dependency to optionally authenticate a user without enforcing token presence."""
    if not credentials or not credentials.credentials:
        return None
    try:
        return await get_current_user(credentials)
    except AuthenticationError:
        return None
