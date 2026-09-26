"""Unit tests for AuthService with mocked Supabase Auth client."""

from unittest.mock import AsyncMock
import pytest

from app.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_auth_service_register() -> None:
    """Verify user registration via AuthService delegates to the auth client."""
    mock_client = AsyncMock()
    mock_client.sign_up.return_value = {
        "user_id": "test-user-id",
        "email": "user@example.com",
        "access_token": "mock-token",
    }
    service = AuthService(auth_client=mock_client)

    result = await service.register_user(
        email="user@example.com",
        password="secretpassword123",
        name="Test User",
    )

    assert result["user_id"] == "test-user-id"
    assert result["email"] == "user@example.com"
    mock_client.sign_up.assert_called_once_with(
        email="user@example.com",
        password="secretpassword123",
        metadata={"name": "Test User"},
    )


@pytest.mark.asyncio
async def test_auth_service_login() -> None:
    """Verify user login via AuthService delegates to the auth client."""
    mock_client = AsyncMock()
    mock_client.sign_in_with_password.return_value = {
        "user_id": "test-user-id",
        "email": "user@example.com",
        "access_token": "mock-token",
    }
    service = AuthService(auth_client=mock_client)

    result = await service.login_user(
        email="user@example.com",
        password="secretpassword123",
    )

    assert result["access_token"] == "mock-token"
    mock_client.sign_in_with_password.assert_called_once_with(
        email="user@example.com",
        password="secretpassword123",
    )
