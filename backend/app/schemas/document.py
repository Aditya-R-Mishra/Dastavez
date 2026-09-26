"""Pydantic schemas for document ingestion, status, and metadata."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.core.constants import DocumentStatus, PageStatus


class DocumentUploadResponse(BaseModel):
    """Response returned immediately upon document file upload."""

    document_id: str
    filename: str
    status: DocumentStatus = DocumentStatus.PROCESSING
    job_id: Optional[str] = None


class DocumentResponse(BaseModel):
    """Document record representation."""

    id: str
    user_id: str
    filename: str
    file_type: str
    file_size: int
    storage_path: Optional[str] = None
    status: DocumentStatus
    total_pages: int = 0
    created_at: datetime
    processed_at: Optional[datetime] = None


class DocumentListResponse(BaseModel):
    """Paginated list of documents."""

    documents: List[DocumentResponse]
    total: int


class DocumentStatusResponse(BaseModel):
    """Real-time processing status of a document and its background job."""

    document_id: str
    status: DocumentStatus
    progress: int = Field(ge=0, le=100)
    current_stage: str
    error_message: Optional[str] = None
    updated_at: Optional[datetime] = None


class PageEvidenceResponse(BaseModel):
    """Extracted text and OCR details for a specific page."""

    id: Optional[str] = None
    document_id: str
    page_number: int
    raw_text: str
    ocr_used: bool
    ocr_engine: str
    language: Optional[str] = None
    page_status: PageStatus
    created_at: Optional[datetime] = None
