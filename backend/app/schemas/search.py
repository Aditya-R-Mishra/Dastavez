"""Pydantic schemas for semantic search endpoints."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Semantic vector search query payload."""

    query: str = Field(min_length=1, description="Natural language search query")
    document_ids: Optional[List[str]] = Field(default=None, description="Optional document ID filter")
    limit: int = Field(default=5, ge=1, le=50, description="Maximum number of chunks to return")
    language: Optional[str] = Field(default=None, description="Language hint if known")


class SearchResultItem(BaseModel):
    """Individual chunk search result item."""

    chunk_id: str
    document_id: str
    filename: Optional[str] = None
    page: Optional[int] = None
    section: Optional[str] = None
    content: str
    score: float
    language: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    """Semantic search response payload."""

    query: str
    results: List[SearchResultItem]
    total_results: int
