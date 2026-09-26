"""Document management and ingestion API endpoints."""

from fastapi import APIRouter, BackgroundTasks, Depends, File, Query, UploadFile, status

from app.core.security import AuthenticatedUser, get_current_user
from app.schemas.common import StandardResponse
from app.schemas.document import (
    DocumentListResponse,
    DocumentResponse,
    DocumentStatusResponse,
    DocumentUploadResponse,
)
from app.services.document_service import DocumentService
from app.workers.processing_worker import run_document_pipeline_task
from app.workers.task_queue import dispatch_processing_task

router = APIRouter(prefix="/documents", tags=["Documents"])


def get_document_service() -> DocumentService:
    """Dependency provider for DocumentService."""
    return DocumentService()


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: AuthenticatedUser = Depends(get_current_user),
    doc_service: DocumentService = Depends(get_document_service),
) -> DocumentUploadResponse:
    """Upload a heterogeneous document for processing and vector indexing."""
    file_bytes = await file.read()
    content_type = file.content_type or "application/octet-stream"

    result = await doc_service.upload_document(
        user_id=current_user.id,
        filename=file.filename or "uploaded_document",
        file_bytes=file_bytes,
        content_type=content_type,
    )

    # Dispatch ingestion pipeline via Celery worker or FastAPI BackgroundTasks
    dispatch_processing_task(
        background_tasks=background_tasks,
        job_id=result["job_id"],
        document_id=result["document_id"],
        user_id=current_user.id,
    )

    return DocumentUploadResponse(
        document_id=result["document_id"],
        filename=result["filename"],
        status=result["status"],
        job_id=result["job_id"],
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: AuthenticatedUser = Depends(get_current_user),
    doc_service: DocumentService = Depends(get_document_service),
) -> DocumentListResponse:
    """List all documents owned by the authenticated user."""
    docs, total = await doc_service.list_documents(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )
    return DocumentListResponse(
        documents=[DocumentResponse(**doc) for doc in docs],
        total=total,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    doc_service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    """Retrieve metadata for a specific document."""
    doc = await doc_service.get_document(document_id, current_user.id)
    return DocumentResponse(**doc)


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    doc_service: DocumentService = Depends(get_document_service),
) -> DocumentStatusResponse:
    """Fetch the real-time processing progress and status of a document."""
    job_status = await doc_service.get_document_status(document_id, current_user.id)
    return DocumentStatusResponse(**job_status)


@router.delete("/{document_id}", response_model=StandardResponse[None])
async def delete_document(
    document_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    doc_service: DocumentService = Depends(get_document_service),
) -> StandardResponse[None]:
    """Delete a document along with all associated pages, chunks, and storage assets."""
    await doc_service.delete_document(document_id, current_user.id)
    return StandardResponse(
        success=True,
        message=f"Document '{document_id}' deleted successfully",
        data=None,
    )
