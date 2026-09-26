"""Integration tests for document management and status endpoints."""

from datetime import datetime, timezone
import time
from unittest.mock import AsyncMock
import jwt
import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.documents import get_document_service
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
async def test_upload_document_route() -> None:
    """Verify POST /api/v1/documents/upload dispatches ingestion job and returns 202."""
    from unittest.mock import patch
    mock_service = AsyncMock()
    mock_service.upload_document.return_value = {
        "document_id": "doc-uuid-1",
        "filename": "sample.pdf",
        "status": "PROCESSING",
        "job_id": "job-uuid-1",
    }
    app.dependency_overrides[get_document_service] = lambda: mock_service

    headers = get_auth_headers()
    files = {"file": ("sample.pdf", b"%PDF-1.4 sample content", "application/pdf")}

    with patch("app.api.v1.documents.dispatch_processing_task") as mock_dispatch:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/documents/upload", files=files, headers=headers)
            assert response.status_code == 202
            mock_dispatch.assert_called_once()
            data = response.json()
            assert data["document_id"] == "doc-uuid-1"
            assert data["filename"] == "sample.pdf"
            assert data["status"] == "PROCESSING"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_document_status_route() -> None:
    """Verify GET /api/v1/documents/{id}/status returns real pipeline stage."""
    mock_service = AsyncMock()
    mock_service.get_document_status.return_value = {
        "document_id": "doc-uuid-1",
        "status": "PROCESSING",
        "progress": 65,
        "current_stage": "Generating embeddings",
        "error_message": None,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    app.dependency_overrides[get_document_service] = lambda: mock_service

    headers = get_auth_headers()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/documents/doc-uuid-1/status", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["progress"] == 65
        assert data["current_stage"] == "Generating embeddings"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_page_evidence_route() -> None:
    """Verify GET /api/v1/documents/{id}/pages/{page} returns page extraction details."""
    mock_service = AsyncMock()
    mock_service.get_page_evidence.return_value = {
        "id": "page-1",
        "document_id": "doc-uuid-1",
        "page_number": 5,
        "raw_text": "Clause 14: Terms of service.",
        "ocr_used": True,
        "ocr_engine": "paddle_ocr",
        "language": "en",
        "page_status": "COMPLETED",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    from app.api.v1.evidence import get_document_service as get_evidence_doc_service
    app.dependency_overrides[get_evidence_doc_service] = lambda: mock_service

    headers = get_auth_headers()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/documents/doc-uuid-1/pages/5", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["page_number"] == 5
        assert data["ocr_used"] is True
        assert data["ocr_engine"] == "paddle_ocr"
        assert "Terms of service" in data["raw_text"]

    app.dependency_overrides.clear()
