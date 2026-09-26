"""Unit tests for DocumentService business logic."""

from unittest.mock import AsyncMock
import pytest

from app.core.exceptions import (
    DocumentAccessDeniedError,
    DocumentNotFoundError,
    FileSizeLimitExceededError,
    InvalidFileTypeError,
)
from app.services.document_service import DocumentService


@pytest.mark.asyncio
async def test_upload_document_success() -> None:
    """Verify document upload orchestration persists records and creates job."""
    mock_doc_repo = AsyncMock()
    mock_job_repo = AsyncMock()
    mock_storage = AsyncMock()

    mock_doc_repo.create_document.return_value = {"id": "doc-uuid-1"}
    mock_job_repo.create_job.return_value = {"id": "job-uuid-1"}
    mock_storage.upload_file.return_value = "storage/path.pdf"

    service = DocumentService(
        doc_repo=mock_doc_repo,
        job_repo=mock_job_repo,
        storage_client=mock_storage,
    )

    result = await service.upload_document(
        user_id="user-123",
        filename="report.pdf",
        file_bytes=b"%PDF-1.4 test bytes",
    )

    assert result["document_id"] == "doc-uuid-1"
    assert result["job_id"] == "job-uuid-1"
    assert result["status"] == "PROCESSING"
    mock_storage.upload_file.assert_called_once()
    mock_doc_repo.create_document.assert_called_once()
    mock_job_repo.create_job.assert_called_once()


@pytest.mark.asyncio
async def test_upload_document_invalid_type() -> None:
    """Verify upload rejects unsupported file types."""
    service = DocumentService()
    with pytest.raises(InvalidFileTypeError):
        await service.upload_document(
            user_id="user-123",
            filename="malware.exe",
            file_bytes=b"MZ...",
        )


@pytest.mark.asyncio
async def test_upload_document_size_exceeded() -> None:
    """Verify upload rejects files larger than maximum size."""
    service = DocumentService()
    huge_bytes = b"x" * (51 * 1024 * 1024)
    with pytest.raises(FileSizeLimitExceededError):
        await service.upload_document(
            user_id="user-123",
            filename="large.pdf",
            file_bytes=huge_bytes,
        )


@pytest.mark.asyncio
async def test_get_document_access_control() -> None:
    """Verify access denial when requesting another user's document."""
    mock_doc_repo = AsyncMock()
    mock_doc_repo.get_document_by_id.return_value = {
        "id": "doc-1",
        "user_id": "other-user",
        "filename": "confidential.pdf",
    }
    service = DocumentService(doc_repo=mock_doc_repo)

    with pytest.raises(DocumentAccessDeniedError):
        await service.get_document("doc-1", user_id="user-attacker")
