"""Unit tests for section-aware text chunking."""

import pytest
from app.services.pipeline.chunking import DocumentChunker


def test_chunker_basic_splitting() -> None:
    """Verify that chunker splits long paragraphs with correct attribution metadata."""
    chunker = DocumentChunker(chunk_size_tokens=20, chunk_overlap_tokens=5)
    sample_text = (
        "## Eligibility Requirements\n\n"
        "Applicants must be at least 18 years of age. They must provide valid government-issued identification.\n\n"
        "All submitted records must be verified by an accredited authority prior to acceptance."
    )
    chunks = chunker.chunk_page(
        document_id="doc-123",
        page_id="page-1",
        page_number=1,
        text=sample_text,
        start_chunk_index=0,
        filename="policy.pdf",
    )

    assert len(chunks) >= 1
    for chunk in chunks:
        assert chunk["document_id"] == "doc-123"
        assert chunk["page_number"] == 1
        assert "metadata" in chunk
        assert chunk["metadata"]["filename"] == "policy.pdf"
        assert chunk["content"] != ""


def test_chunker_empty_input() -> None:
    """Verify that empty text produces no chunks."""
    chunker = DocumentChunker()
    chunks = chunker.chunk_page(
        document_id="doc-123",
        page_id="page-1",
        page_number=1,
        text="   \n\n  ",
    )
    assert chunks == []
