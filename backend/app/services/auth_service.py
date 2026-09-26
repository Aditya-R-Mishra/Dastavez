"""Business logic service for user authentication and authorization."""

from typing import Any, Dict, Optional
from app.integrations.supabase_client import SupabaseAuthClient


class AuthService:
    """Service handling authentication flows and user session lifecycle."""

    def __init__(self, auth_client: Optional[SupabaseAuthClient] = None) -> None:
        self.auth_client = auth_client or SupabaseAuthClient()

    async def register_user(self, email: str, password: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Register a new user account with profile metadata."""
        metadata = {"name": name} if name else {}
        return await self.auth_client.sign_up(email=email, password=password, metadata=metadata)

    async def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user credentials and generate session tokens."""
        return await self.auth_client.sign_in_with_password(email=email, password=password)

    async def get_user_profile(self, token: str) -> Dict[str, Any]:
        """Retrieve user profile information using valid access token."""
        return await self.auth_client.get_user_by_token(token)
