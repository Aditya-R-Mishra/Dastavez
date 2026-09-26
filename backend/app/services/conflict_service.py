"""Conflict detection and insufficient evidence identification service."""

import re
from typing import Any, Dict, List, Optional

from app.core.exceptions import ConflictingInformationError, InsufficientEvidenceError
from app.core.logging import get_logger

logger = get_logger(__name__)


class ConflictService:
    """Detects cross-document contradictions and verifies sufficiency of retrieved evidence."""

    def check_evidence_sufficiency(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        min_relevance_score: float = 0.3,
    ) -> bool:
        """Verify whether retrieved chunks provide sufficient relevance to answer the query."""
        if not retrieved_chunks:
            return False

        # Check if top chunk meets minimal relevance threshold
        top_score = max((c.get("score", 0.0) for c in retrieved_chunks), default=0.0)
        if top_score < min_relevance_score:
            logger.warning(
                "Evidence insufficient: top retrieval score (%.2f) below threshold (%.2f)",
                top_score,
                min_relevance_score,
            )
            return False

        return True

    def find_contradictions(
        self,
        retrieved_chunks: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Identify conflicting numerical assertions or clauses across disparate documents."""
        conflicts: List[Dict[str, Any]] = []
        if len(retrieved_chunks) < 2:
            return conflicts

        # Extract numerical specifications associated with keywords (e.g., age, fee, limit)
        pattern = re.compile(r"\b(age|limit|fee|rate|period|days|years|months|amount)\b[^\.\n]*?(\d+)", re.IGNORECASE)
        facts_by_attribute: Dict[str, List[Dict[str, Any]]] = {}

        for chunk in retrieved_chunks:
            content = chunk.get("content", "")
            doc_name = chunk.get("filename") or chunk.get("document_id") or "Document"
            page = chunk.get("page", 1)

            matches = pattern.findall(content)
            for attr, val in matches:
                attr_key = attr.lower()
                facts_by_attribute.setdefault(attr_key, []).append({
                    "document": doc_name,
                    "page": page,
                    "value": val,
                    "snippet": content[:120],
                })

        # Flag attributes with conflicting numeric values across different sources
        for attr, facts in facts_by_attribute.items():
            unique_values = {f["value"] for f in facts}
            if len(unique_values) > 1 and len(facts) > 1:
                conflicts.append({
                    "attribute": attr,
                    "conflicting_facts": facts,
                })

        return conflicts
