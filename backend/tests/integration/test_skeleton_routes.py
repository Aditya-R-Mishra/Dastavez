"""Integration tests for Phase 1 skeleton routes."""

import time
import jwt
import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.main import app


def get_auth_headers() -> dict:
    """Helper to generate valid authorization header for testing."""
    payload = {
        "sub": "test-user-id",
        "email": "test@example.com",
        "role": "authenticated",
        "user_metadata": {"name": "Test User"},
        "exp": int(time.time()) + 3600,
    }
    token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_skeleton_routes_require_authentication() -> None:
    """Verify that protected skeleton routes reject unauthenticated requests."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        routes_to_test = [
            ("GET", "/api/v1/documents"),
            ("GET", "/api/v1/documents/sample-id"),
            ("GET", "/api/v1/documents/sample-id/status"),
            ("DELETE", "/api/v1/documents/sample-id"),
            ("POST", "/api/v1/search"),
            ("POST", "/api/v1/chat"),
            ("GET", "/api/v1/chat/conversations"),
            ("GET", "/api/v1/documents/sample-id/pages/1"),
            ("POST", "/api/v1/chat/voice"),
        ]
        for method, path in routes_to_test:
            if method == "GET":
                res = await client.get(path)
            elif method == "DELETE":
                res = await client.delete(path)
            elif method == "POST":
                res = await client.post(path, json={})
            assert res.status_code == 401, f"{method} {path} should require authentication"
            assert res.json()["error_code"] == "AUTHENTICATION_FAILED"
