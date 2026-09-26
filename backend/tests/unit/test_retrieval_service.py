"""Unit tests for semantic retrieval service."""

from unittest.mock import AsyncMock, MagicMock
import pytest

from app.services.retrieval_service import RetrievalService


@pytest.mark.asyncio
async def test_retrieval_service_search() -> None:
    """Verify semantic retrieval converts query to vector and extracts structured results."""
    mock_embeddings = AsyncMock()
    mock_embeddings.generate_embedding.return_value = [0.1] * 1024

    mock_point = MagicMock()
    mock_point.id = "chunk-123"
    mock_point.score = 0.92
    mock_point.payload = {
        "document_id": "doc-abc",
        "filename": "policy.pdf",
        "page": 3,
        "section": "Coverage",
        "content": "Eligible expenses include medical bills.",
        "language": "en",
    }

    mock_vector = AsyncMock()
    mock_vector.search.return_value = [mock_point]

    service = RetrievalService(
        vector_client=mock_vector,
        embedding_service=mock_embeddings,
    )

    results = await service.search(query="What are the eligible expenses?", limit=3)

    assert len(results) == 1
    assert results[0]["chunk_id"] == "chunk-123"
    assert results[0]["document_id"] == "doc-abc"
    assert results[0]["dense_score"] == 0.92
    assert results[0]["score"] > 0.0  # Reciprocal rank fused score
    assert "medical bills" in results[0]["content"]
    mock_embeddings.generate_embedding.assert_called_once_with("What are the eligible expenses?")
    mock_vector.search.assert_called_once()
