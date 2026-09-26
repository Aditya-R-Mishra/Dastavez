"""Unit tests for evidence-grounded answer generation service."""

from unittest.mock import AsyncMock
import pytest

from app.services.llm_service import LLMService


@pytest.mark.asyncio
async def test_llm_service_grounded_answer_parsing() -> None:
    """Verify LLMService constructs prompt and parses JSON answer and sources."""
    mock_provider = AsyncMock()
    json_output = (
        '{\n'
        '  "answer": "The maximum entry age is 65 years.",\n'
        '  "sources": [\n'
        '    {"document": "policy.pdf", "page": 12, "section": "Eligibility", "chunk_id": "c-1"}\n'
        '  ]\n'
        '}'
    )
    mock_provider.generate_response.return_value = json_output

    service = LLMService(provider=mock_provider)
    chunks = [{
        "chunk_id": "c-1",
        "filename": "policy.pdf",
        "page": 12,
        "section": "Eligibility",
        "content": "Maximum age for policy entry is 65 years.",
    }]

    answer, sources = await service.generate_grounded_answer(
        query="What is the maximum entry age?",
        retrieved_chunks=chunks,
    )

    assert "65 years" in answer
    assert len(sources) == 1
    assert sources[0]["document"] == "policy.pdf"
    assert sources[0]["page"] == 12
    assert sources[0]["chunk_id"] == "c-1"


@pytest.mark.asyncio
async def test_llm_service_fallback_parsing() -> None:
    """Verify fallback parsing when LLM outputs non-JSON plain text."""
    mock_provider = AsyncMock()
    mock_provider.generate_response.return_value = "Plain text response without JSON wrapper."

    service = LLMService(provider=mock_provider)
    chunks = [{
        "chunk_id": "c-2",
        "filename": "guidelines.pdf",
        "page": 5,
        "section": "General",
        "content": "Sample content",
    }]

    answer, sources = await service.generate_grounded_answer(
        query="Explain guidelines",
        retrieved_chunks=chunks,
    )

    assert answer == "Plain text response without JSON wrapper."
    assert len(sources) == 1
    assert sources[0]["document"] == "guidelines.pdf"
