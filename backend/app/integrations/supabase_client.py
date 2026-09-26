"""Thin client wrapper for Supabase Auth, Database, and Storage interactions."""

from typing import Any, Dict, Optional
from supabase import Client, create_client

from app.core.config import settings
from app.core.exceptions import AuthenticationError, ExternalServiceError
from app.core.logging import get_logger

logger = get_logger(__name__)

_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Retrieve or initialize the singleton Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        try:
            # Use service role key to allow backend service operations
            key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY
            _supabase_client = create_client(settings.SUPABASE_URL, key)
            logger.info("Supabase client initialized successfully")
        except Exception as exc:
            logger.error("Failed to initialize Supabase client: %s", str(exc))
            raise ExternalServiceError("Supabase", str(exc)) from exc
    return _supabase_client


class SupabaseAuthClient:
    """Thin wrapper for Supabase Auth interactions."""

    def __init__(self, client: Optional[Client] = None) -> None:
        self.client = client or get_supabase_client()

    async def sign_up(self, email: str, password: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Register a new user with Supabase Auth, ensuring immediate email confirmation and session token."""
        try:
            # 1. Attempt admin creation with auto-confirmed email if service role is active
            if hasattr(self.client.auth, "admin") and hasattr(self.client.auth.admin, "create_user"):
                try:
                    admin_res = self.client.auth.admin.create_user({
                        "email": email,
                        "password": password,
                        "email_confirm": True,
                        "user_metadata": metadata or {},
                    })
                    if admin_res and admin_res.user:
                        # Immediately sign in to obtain access token
                        return await self.sign_in_with_password(email=email, password=password)
                except Exception as admin_exc:
                    logger.info("Admin create_user fallback to standard sign_up: %s", str(admin_exc))

            # 2. Standard sign-up fallback
            options: Dict[str, Any] = {}
            if metadata:
                options["data"] = metadata
            response = self.client.auth.sign_up({"email": email, "password": password, "options": options})
            user = response.user
            session = response.session

            if not session:
                # Try signing in immediately if user was already confirmed or auto-confirmed
                try:
                    return await self.sign_in_with_password(email=email, password=password)
                except Exception:
                    pass

            return {
                "user_id": str(user.id) if user else "",
                "email": user.email if user else email,
                "access_token": session.access_token if session else "",
            }
        except Exception as exc:
            logger.warning("Supabase sign_up failed for email %s: %s", email, str(exc))
            raise AuthenticationError(f"Registration failed: {str(exc)}") from exc

    async def sign_in_with_password(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user credentials with Supabase Auth."""
        try:
            response = self.client.auth.sign_in_with_password({"email": email, "password": password})
            user = response.user
            session = response.session
            if not session:
                raise AuthenticationError("No session returned from authentication")
            return {
                "user_id": str(user.id) if user else "",
                "email": user.email if user else email,
                "access_token": session.access_token,
            }
        except Exception as exc:
            logger.warning("Supabase sign_in failed for email %s: %s", email, str(exc))
            raise AuthenticationError(f"Login failed: {str(exc)}") from exc

    async def get_user_by_token(self, token: str) -> Dict[str, Any]:
        """Fetch user profile details from Supabase using access token."""
        try:
            response = self.client.auth.get_user(token)
            user = response.user
            if not user:
                raise AuthenticationError("User not found for provided token")
            return {
                "id": str(user.id),
                "email": user.email or "",
                "user_metadata": user.user_metadata or {},
                "created_at": getattr(user, "created_at", None),
            }
        except Exception as exc:
            raise AuthenticationError("Could not retrieve user session") from exc


class SupabaseStorageClient:
    """Thin wrapper for Supabase Storage interactions."""

    def __init__(self, client: Optional[Client] = None, bucket_name: Optional[str] = None) -> None:
        self.client = client or get_supabase_client()
        self.bucket_name = bucket_name or settings.SUPABASE_STORAGE_BUCKET

    async def upload_file(self, file_path: str, file_bytes: bytes, content_type: str) -> str:
        """Upload a file to Supabase Storage and return storage path."""
        try:
            self.client.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=file_bytes,
                file_options={"content-type": content_type, "upsert": "true"},
            )
            return file_path
        except Exception as exc:
            logger.error("Failed to upload file %s to bucket %s: %s", file_path, self.bucket_name, str(exc))
            raise ExternalServiceError("Supabase Storage", str(exc)) from exc

    async def download_file(self, file_path: str) -> bytes:
        """Download file bytes from Supabase Storage."""
        try:
            response = self.client.storage.from_(self.bucket_name).download(file_path)
            return response
        except Exception as exc:
            logger.error("Failed to download file %s from bucket %s: %s", file_path, self.bucket_name, str(exc))
            raise ExternalServiceError("Supabase Storage", str(exc)) from exc

    async def delete_file(self, file_path: str) -> None:
        """Delete a file from Supabase Storage."""
        try:
            self.client.storage.from_(self.bucket_name).remove([file_path])
        except Exception as exc:
            logger.error("Failed to delete file %s from bucket %s: %s", file_path, self.bucket_name, str(exc))
            raise ExternalServiceError("Supabase Storage", str(exc)) from exc
