"""Integration tests for search API routes."""

import time
from unittest.mock import AsyncMock
import jwt
import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.search import get_retrieval_service
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
async def test_search_route_success() -> None:
    """Verify POST /api/v1/search returns matching chunk items."""
    mock_retrieval = AsyncMock()
    mock_retrieval.search.return_value = [
        {
            "chunk_id": "c-101",
            "document_id": "doc-500",
            "filename": "guidelines.pdf",
            "page": 2,
            "section": "Eligibility",
            "content": "Applicants must be at least 18.",
            "score": 0.89,
            "language": "en",
            "metadata": {},
        }
    ]
    app.dependency_overrides[get_retrieval_service] = lambda: mock_retrieval

    headers = get_auth_headers()
    payload = {"query": "eligibility criteria", "limit": 5}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/search", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "eligibility criteria"
        assert data["total_results"] == 1
        assert data["results"][0]["chunk_id"] == "c-101"
        assert data["results"][0]["score"] == 0.89

    app.dependency_overrides.clear()
