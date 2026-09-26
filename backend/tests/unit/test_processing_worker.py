"""Unit tests for background document processing worker and idempotency."""

from unittest.mock import AsyncMock, patch
import pytest

from app.core.constants import DocumentStatus, PageStatus
from app.services.pipeline.text_extraction import ExtractedPage
from app.workers.processing_worker import DocumentProcessingWorker


@pytest.mark.asyncio
async def test_worker_processes_document_end_to_end() -> None:
    """Verify background worker processes all pipeline stages to completion."""
    mock_doc_repo = AsyncMock()
    mock_job_repo = AsyncMock()
    mock_chunk_repo = AsyncMock()
    mock_storage = AsyncMock()
    mock_vector = AsyncMock()
    mock_embeddings = AsyncMock()

    mock_doc_repo.get_document_by_id.return_value = {
        "id": "doc-123",
        "filename": "guide.txt",
        "file_type": "txt",
        "storage_path": "user/doc-123/guide.txt",
    }
    mock_storage.download_file.return_value = b"Hello document intelligence world."
    mock_doc_repo.get_pages_by_document.return_value = []
    mock_doc_repo.create_or_update_page.return_value = {"id": "page-1", "page_number": 1}
    mock_embeddings.generate_embeddings.return_value = [[0.1] * 1024]

    worker = DocumentProcessingWorker(
        doc_repo=mock_doc_repo,
        job_repo=mock_job_repo,
        chunk_repo=mock_chunk_repo,
        storage_client=mock_storage,
        vector_client=mock_vector,
        embedding_service=mock_embeddings,
    )

    await worker.process_document(document_id="doc-123", job_id="job-456", user_id="user-1")

    mock_doc_repo.update_document_status.assert_called_with(
        document_id="doc-123",
        status=DocumentStatus.COMPLETED.value,
        total_pages=1,
        processed_at=pytest.approx(mock_doc_repo.update_document_status.call_args[1].get("processed_at")),
    )
    mock_vector.upsert_chunks.assert_called_once()


@pytest.mark.asyncio
async def test_worker_idempotency_skips_completed_pages() -> None:
    """Verify worker skips re-extracting pages already marked COMPLETED."""
    mock_doc_repo = AsyncMock()
    mock_job_repo = AsyncMock()
    mock_chunk_repo = AsyncMock()
    mock_storage = AsyncMock()
    mock_vector = AsyncMock()
    mock_embeddings = AsyncMock()

    mock_doc_repo.get_document_by_id.return_value = {
        "id": "doc-123",
        "filename": "guide.txt",
        "file_type": "txt",
        "storage_path": "user/doc-123/guide.txt",
    }
    mock_storage.download_file.return_value = b"Already processed text."

    # Page 1 is already completed
    mock_doc_repo.get_pages_by_document.return_value = [
        {"id": "p-1", "page_number": 1, "raw_text": "Already processed text.", "page_status": PageStatus.COMPLETED.value}
    ]
    mock_embeddings.generate_embeddings.return_value = [[0.1] * 1024]

    worker = DocumentProcessingWorker(
        doc_repo=mock_doc_repo,
        job_repo=mock_job_repo,
        chunk_repo=mock_chunk_repo,
        storage_client=mock_storage,
        vector_client=mock_vector,
        embedding_service=mock_embeddings,
    )

    await worker.process_document(document_id="doc-123", job_id="job-456", user_id="user-1")

    # create_or_update_page should NOT be called for completed page 1
    mock_doc_repo.create_or_update_page.assert_not_called()
