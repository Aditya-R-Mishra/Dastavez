"""Unit tests for hybrid retrieval and Reciprocal Rank Fusion (RRF)."""

from unittest.mock import AsyncMock, MagicMock
import pytest

from app.services.retrieval_service import RetrievalService


@pytest.mark.asyncio
async def test_hybrid_retrieval_fuses_dense_and_sparse_scores() -> None:
    """Verify RRF re-ranks documents considering both vector similarity and lexical overlap."""
    mock_embeddings = AsyncMock()
    mock_embeddings.generate_embedding.return_value = [0.0] * 1024

    # Chunk A has higher dense score, but low lexical match with query
    chunk_a = MagicMock()
    chunk_a.id = "chunk-a"
    chunk_a.score = 0.95
    chunk_a.payload = {
        "document_id": "doc-1",
        "content": "Unrelated words completely outside the vocabulary of interest",
    }

    # Chunk B has slightly lower dense score, but high lexical match with query terms
    chunk_b = MagicMock()
    chunk_b.id = "chunk-b"
    chunk_b.score = 0.88
    chunk_b.payload = {
        "document_id": "doc-2",
        "content": "Claim settlement turnaround time for policyholders under emergency conditions",
    }

    mock_vector = AsyncMock()
    mock_vector.search.return_value = [chunk_a, chunk_b]

    service = RetrievalService(vector_client=mock_vector, embedding_service=mock_embeddings)

    results = await service.search(
        query="emergency claim settlement turnaround time",
        limit=2,
        use_hybrid_fusion=True,
    )

    assert len(results) == 2
    # Verify that both chunks received an RRF score
    assert "score" in results[0]
    assert "dense_score" in results[0]
    # Chunk B should rank first due to strong sparse keyword reinforcement
    assert results[0]["chunk_id"] == "chunk-b"


def test_compute_sparse_lexical_score() -> None:
    """Verify sparse lexical scoring calculates normalized term match frequency."""
    service = RetrievalService(vector_client=MagicMock(), embedding_service=MagicMock())
    score_high = service._compute_sparse_lexical_score(
        query="maternity insurance coverage",
        content="This policy provides full maternity insurance coverage for all treatments",
    )
    score_low = service._compute_sparse_lexical_score(
        query="maternity insurance coverage",
        content="General vehicle maintenance terms and conditions",
    )
    assert score_high > score_low
    assert score_low == 0.0
