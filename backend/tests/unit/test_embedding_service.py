"""Unit tests for dense multilingual embedding service."""

from unittest.mock import MagicMock, patch
import pytest

from app.services.embedding_service import EmbeddingService


@pytest.mark.asyncio
async def test_generate_single_embedding_with_mock_model() -> None:
    """Verify single embedding generation with mocked SentenceTransformer."""
    mock_model = MagicMock()
    # Return 1024-dim embedding
    mock_model.encode.return_value = [[0.05] * 1024]

    service = EmbeddingService()
    with patch.object(service, "_get_model", return_value=mock_model):
        vec = await service.generate_embedding("Test semantic text chunk")

    assert len(vec) == 1024
    assert vec[0] == 0.05


@pytest.mark.asyncio
async def test_generate_fallback_embedding() -> None:
    """Verify fallback embedding generates deterministic 1024-dim vector."""
    service = EmbeddingService()
    # Force fallback by setting _get_model to return None
    with patch.object(service, "_get_model", return_value=None):
        vec = await service.generate_embedding("Offline test chunk")

    assert len(vec) == 1024
    assert any(v != 0.0 for v in vec)
