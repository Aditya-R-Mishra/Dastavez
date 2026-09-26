"""Hybrid semantic and sparse retrieval service with Reciprocal Rank Fusion (RRF) and reranking."""

import math
from typing import Any, Dict, List, Optional

from app.core.logging import get_logger
from app.integrations.qdrant_client import QdrantVectorClient
from app.repositories.document_repository import DocumentRepository
from app.services.embedding_service import EmbeddingService

logger = get_logger(__name__)


class RetrievalService:
    """Service performing hybrid dense-sparse vector retrieval and fusion reranking."""

    def __init__(
        self,
        vector_client: Optional[QdrantVectorClient] = None,
        embedding_service: Optional[EmbeddingService] = None,
        doc_repo: Optional[DocumentRepository] = None,
    ) -> None:
        self.vector_client = vector_client or QdrantVectorClient()
        self.embedding_service = embedding_service or EmbeddingService()
        self.doc_repo = doc_repo or DocumentRepository()

    def _compute_sparse_lexical_score(self, query: str, content: str) -> float:
        """Compute keyword relevance score using token frequency and length normalization."""
        q_tokens = set(query.lower().split())
        if not q_tokens or not content:
            return 0.0

        c_tokens = content.lower().split()
        if not c_tokens:
            return 0.0

        matched = sum(1 for token in c_tokens if token in q_tokens)
        # Term frequency normalized by doc length
        return matched / math.sqrt(len(c_tokens))

    def _reciprocal_rank_fusion(
        self,
        dense_results: List[Dict[str, Any]],
        sparse_scores: Dict[str, float],
        k: int = 60,
    ) -> List[Dict[str, Any]]:
        """Combine dense and sparse rankings using Reciprocal Rank Fusion (RRF)."""
        rrf_scores: Dict[str, float] = {}

        # 1. Rank by dense similarity
        dense_sorted = sorted(dense_results, key=lambda x: x["score"], reverse=True)
        for rank, item in enumerate(dense_sorted, 1):
            cid = item["chunk_id"]
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k + rank))

        # 2. Rank by sparse lexical similarity (only documents with positive lexical match)
        lexical_matches = [item for item in dense_results if sparse_scores.get(item["chunk_id"], 0.0) > 0.0]
        sparse_sorted = sorted(lexical_matches, key=lambda x: sparse_scores.get(x["chunk_id"], 0.0), reverse=True)
        for rank, item in enumerate(sparse_sorted, 1):
            cid = item["chunk_id"]
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k + rank))

        # 3. Apply fused score and sort
        for item in dense_results:
            item["score"] = round(rrf_scores.get(item["chunk_id"], item["score"]), 4)

        return sorted(dense_results, key=lambda x: x["score"], reverse=True)

    async def search(
        self,
        query: str,
        user_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
        limit: int = 5,
        language: Optional[str] = None,
        use_hybrid_fusion: bool = True,
    ) -> List[Dict[str, Any]]:
        """Retrieve and rerank semantically and lexically relevant document chunks."""
        logger.info(
            "Executing hybrid retrieval for query: '%s' (scope: %s)",
            query,
            document_ids or "all user documents",
        )

        # Generate dense query embedding vector
        query_vector = await self.embedding_service.generate_embedding(query)

        # Retrieve candidates from Qdrant
        fetch_limit = limit * 2 if use_hybrid_fusion else limit
        raw_results = await self.vector_client.search(
            query_vector=query_vector,
            document_ids=document_ids,
            limit=fetch_limit,
        )

        candidates: List[Dict[str, Any]] = []
        sparse_scores: Dict[str, float] = {}

        for scored_point in raw_results:
            payload = getattr(scored_point, "payload", {}) or {}
            chunk_content = payload.get("content") or payload.get("text", "")
            cid = str(getattr(scored_point, "id", ""))
            dense_s = float(getattr(scored_point, "score", 0.0))
            candidates.append({
                "chunk_id": cid,
                "document_id": str(payload.get("document_id", "")),
                "filename": payload.get("filename"),
                "page": payload.get("page"),
                "section": payload.get("section"),
                "content": chunk_content,
                "score": dense_s,
                "dense_score": dense_s,
                "language": payload.get("language") or language,
                "metadata": payload,
            })
            sparse_scores[cid] = self._compute_sparse_lexical_score(query, chunk_content)

        if use_hybrid_fusion and candidates:
            candidates = self._reciprocal_rank_fusion(candidates, sparse_scores)

        return candidates[:limit]
