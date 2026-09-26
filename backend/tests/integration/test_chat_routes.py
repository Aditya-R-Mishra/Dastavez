"""Integration tests for chat conversations and message routing."""

from datetime import datetime, timezone
import time
from unittest.mock import AsyncMock
import jwt
import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.chat import get_chat_service
from app.core.config import settings
from app.main import app


def get_auth_headers(user_id: str = "user-123") -> dict:
    """Generate authenticated user Bearer token header."""
    payload = {
        "sub": user_id,
        "email": "user@example.com",
        "role": "authenticated",
        "user_metadata": {"name": "Test User"},
        "exp": int(time.time()) + 3600,
    }
    token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_chat_endpoint() -> None:
    """Verify POST /api/v1/chat returns grounded response with sources."""
    mock_service = AsyncMock()
    mock_service.send_message.return_value = {
        "answer": "The maximum entry age is 65 years.",
        "conversation_id": "conv-123",
        "sources": [
            {"document": "Policy.pdf", "page": 12, "section": "Eligibility", "chunk_id": "abc123"}
        ],
        "detected_language": "en",
    }
    app.dependency_overrides[get_chat_service] = lambda: mock_service

    headers = get_auth_headers()
    payload = {"message": "What is the maximum entry age?"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/chat", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "65 years" in data["answer"]
        assert data["conversation_id"] == "conv-123"
        assert len(data["sources"]) == 1
        assert data["sources"][0]["document"] == "Policy.pdf"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_conversations_endpoint() -> None:
    """Verify GET /api/v1/chat/conversations returns user threads."""
    mock_service = AsyncMock()
    mock_service.list_conversations.return_value = (
        [
            {
                "id": "conv-1",
                "user_id": "user-123",
                "title": "First Conversation",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        ],
        1,
    )
    app.dependency_overrides[get_chat_service] = lambda: mock_service

    headers = get_auth_headers()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/chat/conversations", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["conversations"][0]["id"] == "conv-1"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_conversation_detail_endpoint() -> None:
    """Verify GET /api/v1/chat/{conversation_id} returns conversation and messages."""
    mock_service = AsyncMock()
    now_iso = datetime.now(timezone.utc).isoformat()
    mock_service.get_conversation.return_value = {
        "conversation": {
            "id": "conv-1",
            "user_id": "user-123",
            "title": "Topic",
            "created_at": now_iso,
        },
        "messages": [
            {
                "id": "msg-1",
                "conversation_id": "conv-1",
                "role": "user",
                "content": "Hi",
                "input_mode": "text",
                "language": "en",
                "audio_url": None,
                "created_at": now_iso,
            }
        ],
    }
    app.dependency_overrides[get_chat_service] = lambda: mock_service

    headers = get_auth_headers()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/chat/conv-1", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["conversation"]["id"] == "conv-1"
        assert len(data["messages"]) == 1
        assert data["messages"][0]["content"] == "Hi"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_conversation_endpoint() -> None:
    """Verify DELETE /api/v1/chat/{conversation_id} removes conversation thread."""
    mock_service = AsyncMock()
    mock_service.delete_conversation.return_value = True
    app.dependency_overrides[get_chat_service] = lambda: mock_service

    headers = get_auth_headers()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.delete("/api/v1/chat/conv-1", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    app.dependency_overrides.clear()
