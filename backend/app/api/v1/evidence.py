"""Page-level document evidence inspection API endpoints."""

from fastapi import APIRouter, Depends

from app.core.security import AuthenticatedUser, get_current_user
from app.schemas.document import PageEvidenceResponse
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Evidence"])


def get_document_service() -> DocumentService:
    """Dependency provider for DocumentService."""
    return DocumentService()


@router.get("/{document_id}/pages/{page}", response_model=PageEvidenceResponse)
async def get_page_evidence(
    document_id: str,
    page: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    doc_service: DocumentService = Depends(get_document_service),
) -> PageEvidenceResponse:
    """Retrieve raw extracted text, OCR engine, and processing status for an exact document page."""
    page_data = await doc_service.get_page_evidence(document_id, page, current_user.id)
    return PageEvidenceResponse(
        id=str(page_data.get("id", "")),
        document_id=document_id,
        page_number=page_data["page_number"],
        raw_text=page_data["raw_text"],
        ocr_used=page_data["ocr_used"],
        ocr_engine=page_data["ocr_engine"],
        language=page_data.get("language"),
        page_status=page_data["page_status"],
        created_at=page_data.get("created_at"),
    )
