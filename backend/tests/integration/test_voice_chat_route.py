"""Integration tests for POST /api/v1/chat/voice endpoint."""

import time
from unittest.mock import AsyncMock
import jwt
import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.chat import get_voice_service
from app.core.config import settings
from app.main import app


def get_auth_headers() -> dict:
    """Helper to generate valid authorization header for testing."""
    payload = {
        "sub": "voice-user-123",
        "email": "voice@example.com",
        "role": "authenticated",
        "user_metadata": {"name": "Voice User"},
        "exp": int(time.time()) + 3600,
    }
    token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_voice_chat_endpoint_success() -> None:
    """Verify POST /api/v1/chat/voice accepts audio file and returns transcribed answer."""
    mock_voice_service = AsyncMock()
    mock_voice_service.process_voice_query.return_value = {
        "transcript": "What is the policy tenure?",
        "detected_language": "en-IN",
        "answer": "The tenure is 5 years.",
        "conversation_id": "conv-voice-999",
        "sources": [
            {
                "document": "policy.pdf",
                "page": 2,
                "section": "Tenure",
                "chunk_id": "chunk-1",
            }
        ],
        "audio_reply_url": None,
    }

    app.dependency_overrides[get_voice_service] = lambda: mock_voice_service

    try:
        headers = get_auth_headers()
        files = {"file": ("query.wav", b"RIFF1234WAVEfmt...", "audio/wav")}

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.post("/api/v1/chat/voice", files=files, headers=headers)

        assert res.status_code == 200
        data = res.json()
        assert data["transcript"] == "What is the policy tenure?"
        assert data["answer"] == "The tenure is 5 years."
        assert data["detected_language"] == "en-IN"
        assert len(data["sources"]) == 1
        assert data["sources"][0]["document"] == "policy.pdf"
    finally:
        app.dependency_overrides.pop(get_voice_service, None)


@pytest.mark.asyncio
async def test_voice_chat_unauthenticated_fails() -> None:
    """Verify POST /api/v1/chat/voice rejects requests without credentials."""
    files = {"file": ("query.wav", b"RIFF1234WAVEfmt...", "audio/wav")}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/api/v1/chat/voice", files=files)

    assert res.status_code == 401
    assert res.json()["error_code"] == "AUTHENTICATION_FAILED"
