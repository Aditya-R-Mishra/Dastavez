"""Semantic and multi-source document search API endpoints."""

from fastapi import APIRouter, Depends

from app.core.security import AuthenticatedUser, get_current_user
from app.schemas.search import SearchRequest, SearchResponse, SearchResultItem
from app.services.retrieval_service import RetrievalService

router = APIRouter(prefix="/search", tags=["Search"])


def get_retrieval_service() -> RetrievalService:
    """Dependency provider for RetrievalService."""
    return RetrievalService()


@router.post("", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
) -> SearchResponse:
    """Execute semantic vector search across indexed document chunks."""
    results = await retrieval_service.search(
        query=request.query,
        user_id=current_user.id,
        document_ids=request.document_ids,
        limit=request.limit,
        language=request.language,
    )
    items = [SearchResultItem(**item) for item in results]
    return SearchResponse(
        query=request.query,
        results=items,
        total_results=len(items),
    )
