"""Unit tests for ConflictService."""

import pytest

from app.services.conflict_service import ConflictService


def test_evidence_sufficiency_with_good_score() -> None:
    """Verify evidence is deemed sufficient when score meets threshold."""
    service = ConflictService()
    chunks = [{"score": 0.85, "content": "Relevant content"}]
    assert service.check_evidence_sufficiency(query="Test", retrieved_chunks=chunks, min_relevance_score=0.3) is True


def test_evidence_sufficiency_with_low_score_or_empty() -> None:
    """Verify evidence is deemed insufficient when score is below threshold or empty."""
    service = ConflictService()
    assert service.check_evidence_sufficiency(query="Test", retrieved_chunks=[], min_relevance_score=0.3) is False

    low_chunks = [{"score": 0.15, "content": "Vague content"}]
    assert service.check_evidence_sufficiency(query="Test", retrieved_chunks=low_chunks, min_relevance_score=0.3) is False


def test_find_contradictions_detects_numeric_conflict() -> None:
    """Verify find_contradictions flags divergent facts across documents."""
    service = ConflictService()
    chunks = [
        {
            "document_id": "doc-1",
            "filename": "policy_v1.pdf",
            "page": 2,
            "content": "The maximum age is 60 for applicants.",
        },
        {
            "document_id": "doc-2",
            "filename": "policy_v2.pdf",
            "page": 4,
            "content": "The maximum age is 65 for applicants.",
        },
    ]

    conflicts = service.find_contradictions(chunks)
    assert len(conflicts) == 1
    assert conflicts[0]["attribute"] == "age"
    assert len(conflicts[0]["conflicting_facts"]) == 2


def test_find_contradictions_no_conflict_when_matching() -> None:
    """Verify find_contradictions returns empty list when documents agree."""
    service = ConflictService()
    chunks = [
        {"filename": "doc_a.pdf", "page": 1, "content": "The fee is 500 dollars."},
        {"filename": "doc_b.pdf", "page": 1, "content": "The fee is 500 dollars."},
    ]
    conflicts = service.find_contradictions(chunks)
    assert conflicts == []
