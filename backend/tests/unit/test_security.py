"""Unit tests for Supabase JWT authentication decoding and validation."""

import time
import jwt
import pytest

from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.core.security import decode_supabase_jwt


def test_decode_valid_jwt() -> None:
    """Verify that a properly signed Supabase JWT decodes successfully."""
    payload = {
        "sub": "user-uuid-12345",
        "email": "test@example.com",
        "role": "authenticated",
        "user_metadata": {"name": "Test User"},
        "exp": int(time.time()) + 3600,
    }
    token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")
    user = decode_supabase_jwt(token)

    assert user.id == "user-uuid-12345"
    assert user.email == "test@example.com"
    assert user.user_metadata["name"] == "Test User"


def test_decode_expired_jwt() -> None:
    """Verify that an expired JWT raises an AuthenticationError."""
    payload = {
        "sub": "user-uuid-12345",
        "email": "test@example.com",
        "exp": int(time.time()) - 3600,
    }
    token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")

    with pytest.raises(AuthenticationError) as exc_info:
        decode_supabase_jwt(token)
    assert "expired" in str(exc_info.value.message).lower()


def test_decode_invalid_signature_jwt() -> None:
    """Verify that a token with an invalid signature raises an AuthenticationError."""
    payload = {
        "sub": "user-uuid-12345",
        "email": "test@example.com",
        "exp": int(time.time()) + 3600,
    }
    token = jwt.encode(payload, "wrong-secret-key-12345678901234567890", algorithm="HS256")

    with pytest.raises(AuthenticationError) as exc_info:
        decode_supabase_jwt(token)
    assert "invalid" in str(exc_info.value.message).lower()
