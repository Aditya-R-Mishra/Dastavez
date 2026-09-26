"""Business logic service orchestrating document ingestion, status, and lifecycle."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import settings
from app.core.constants import DocumentStatus, ProcessingStage, SupportedFileType
from app.core.exceptions import (
    DocumentAccessDeniedError,
    DocumentNotFoundError,
    FileSizeLimitExceededError,
    InvalidFileTypeError,
)
from app.core.logging import get_logger
from app.integrations.qdrant_client import QdrantVectorClient
from app.integrations.supabase_client import SupabaseStorageClient
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.job_repository import JobRepository

logger = get_logger(__name__)


class DocumentService:
    """Service handling document upload orchestration, access validation, and status tracking."""

    def __init__(
        self,
        doc_repo: Optional[DocumentRepository] = None,
        job_repo: Optional[JobRepository] = None,
        chunk_repo: Optional[ChunkRepository] = None,
        storage_client: Optional[SupabaseStorageClient] = None,
        vector_client: Optional[QdrantVectorClient] = None,
    ) -> None:
        self.doc_repo = doc_repo or DocumentRepository()
        self.job_repo = job_repo or JobRepository()
        self.chunk_repo = chunk_repo or ChunkRepository()
        self.storage_client = storage_client or SupabaseStorageClient()
        self.vector_client = vector_client or QdrantVectorClient()

    def _validate_file(self, filename: str, file_size: int) -> str:
        """Validate uploaded file size and allowed extension."""
        if file_size > settings.MAX_FILE_SIZE_BYTES:
            raise FileSizeLimitExceededError(settings.MAX_FILE_SIZE_BYTES)

        parts = filename.rsplit(".", 1)
        if len(parts) < 2:
            raise InvalidFileTypeError("unknown", [f.value for f in SupportedFileType])

        ext = parts[1].lower()
        valid_extensions = [f.value for f in SupportedFileType]
        if ext not in valid_extensions:
            raise InvalidFileTypeError(ext, valid_extensions)

        return ext

    async def upload_document(
        self,
        user_id: str,
        filename: str,
        file_bytes: bytes,
        content_type: str = "application/octet-stream",
    ) -> Dict[str, Any]:
        """Validate, store, and initialize ingestion records for an uploaded document."""
        file_type = self._validate_file(filename, len(file_bytes))
        document_id = str(uuid.uuid4())
        storage_path = f"{user_id}/{document_id}/{filename}"

        logger.info(
            "Initiating upload for document %s (user: %s, size: %d bytes)",
            filename,
            user_id,
            len(file_bytes),
            extra={"document_id": document_id, "user_id": user_id},
        )

        # Upload file to Supabase Storage
        await self.storage_client.upload_file(
            file_path=storage_path,
            file_bytes=file_bytes,
            content_type=content_type,
        )

        # Create Document record
        doc_record = await self.doc_repo.create_document(
            user_id=user_id,
            filename=filename,
            file_type=file_type,
            file_size=len(file_bytes),
            storage_path=storage_path,
            status=DocumentStatus.PROCESSING.value,
        )

        actual_doc_id = str(doc_record.get("id", document_id))

        # Create initial processing job record
        job_record = await self.job_repo.create_job(
            document_id=actual_doc_id,
            status=DocumentStatus.PROCESSING.value,
            progress=0,
            current_stage=ProcessingStage.UPLOADED.value,
        )

        return {
            "document_id": actual_doc_id,
            "filename": filename,
            "status": DocumentStatus.PROCESSING.value,
            "job_id": str(job_record.get("id", "")),
            "storage_path": storage_path,
        }

    async def list_documents(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Retrieve paginated list of user documents."""
        return await self.doc_repo.list_documents(user_id=user_id, limit=limit, offset=offset)

    async def get_document(self, document_id: str, user_id: str) -> Dict[str, Any]:
        """Retrieve document metadata, validating user access."""
        doc = await self.doc_repo.get_document_by_id(document_id)
        if not doc:
            raise DocumentNotFoundError(document_id)
        if str(doc.get("user_id")) != user_id:
            raise DocumentAccessDeniedError(document_id)
        return doc

    async def get_document_status(self, document_id: str, user_id: str) -> Dict[str, Any]:
        """Fetch processing status and progress for a document."""
        await self.get_document(document_id, user_id)
        job = await self.job_repo.get_latest_job_by_document(document_id)
        if not job:
            return {
                "document_id": document_id,
                "status": DocumentStatus.UPLOADED.value,
                "progress": 0,
                "current_stage": ProcessingStage.UPLOADED.value,
                "error_message": None,
                "updated_at": None,
            }

        return {
            "document_id": document_id,
            "status": job.get("status", DocumentStatus.PROCESSING.value),
            "progress": job.get("progress", 0),
            "current_stage": job.get("current_stage", ProcessingStage.UPLOADED.value),
            "error_message": job.get("error_message"),
            "updated_at": job.get("updated_at"),
        }

    async def get_page_evidence(self, document_id: str, page_number: int, user_id: str) -> Dict[str, Any]:
        """Retrieve page extraction text and OCR details."""
        await self.get_document(document_id, user_id)
        page = await self.doc_repo.get_page_by_number(document_id, page_number)
        if not page:
            raise DocumentNotFoundError(f"{document_id}#page-{page_number}")
        return page

    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete document file, vector points, and database rows."""
        doc = await self.get_document(document_id, user_id)
        storage_path = doc.get("storage_path")

        # Delete from Supabase Storage
        if storage_path:
            try:
                await self.storage_client.delete_file(storage_path)
            except Exception as exc:
                logger.warning("Storage file deletion failed for %s: %s", storage_path, str(exc))

        # Delete vectors from Qdrant
        try:
            await self.vector_client.delete_by_document_id(document_id)
        except Exception as exc:
            logger.warning("Vector point deletion failed for %s: %s", document_id, str(exc))

        # Delete from database
        return await self.doc_repo.delete_document(document_id, user_id)
