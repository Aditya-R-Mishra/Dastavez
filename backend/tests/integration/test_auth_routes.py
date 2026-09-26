"""Integration tests for authentication API endpoints."""

import time
from unittest.mock import AsyncMock
import jwt
import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.auth import get_auth_service
from app.core.config import settings
from app.main import app


def create_test_token(user_id: str = "test-user-id", email: str = "test@example.com") -> str:
    """Generate a signed test JWT."""
    payload = {
        "sub": user_id,
        "email": email,
        "role": "authenticated",
        "user_metadata": {"name": "Test User"},
        "exp": int(time.time()) + 3600,
    }
    return jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")


@pytest.mark.asyncio
async def test_auth_register_route() -> None:
    """Verify POST /api/v1/auth/register endpoint."""
    mock_auth_service = AsyncMock()
    mock_auth_service.register_user.return_value = {
        "user_id": "new-user-123",
        "email": "newuser@example.com",
        "access_token": "token-xyz",
    }
    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "validpassword123",
                "name": "New User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == "new-user-123"
        assert data["email"] == "newuser@example.com"
        assert data["access_token"] == "token-xyz"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_auth_login_route() -> None:
    """Verify POST /api/v1/auth/login endpoint."""
    mock_auth_service = AsyncMock()
    mock_auth_service.login_user.return_value = {
        "user_id": "user-123",
        "email": "user@example.com",
        "access_token": "token-abc",
    }
    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "user@example.com",
                "password": "validpassword123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "user-123"
        assert data["access_token"] == "token-abc"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_me_without_token() -> None:
    """Verify GET /api/v1/auth/me rejects unauthenticated requests with 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401
        data = response.json()
        assert data["error_code"] == "AUTHENTICATION_FAILED"


@pytest.mark.asyncio
async def test_get_me_with_valid_token() -> None:
    """Verify GET /api/v1/auth/me returns user context for valid token."""
    token = create_test_token(user_id="user-xyz-456", email="me@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "user-xyz-456"
        assert data["email"] == "me@example.com"
        assert data["name"] == "Test User"
