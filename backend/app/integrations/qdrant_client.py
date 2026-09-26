"""Thin integration client for Qdrant vector search operations."""

from typing import Any, Dict, List, Optional
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger

logger = get_logger(__name__)

_qdrant_client = None


def get_qdrant_client():
    """Retrieve or initialize the singleton QdrantClient instance."""
    global _qdrant_client
    if _qdrant_client is None:
        try:
            from qdrant_client import QdrantClient

            kwargs: Dict[str, Any] = {
                "url": settings.QDRANT_URL,
                "check_compatibility": False,
            }
            if settings.QDRANT_API_KEY and settings.QDRANT_API_KEY != "your-qdrant-api-key":
                kwargs["api_key"] = settings.QDRANT_API_KEY
            _qdrant_client = QdrantClient(**kwargs)
            logger.info("Connected to Qdrant at %s", settings.QDRANT_URL)
        except Exception as exc:
            logger.error("Failed to initialize Qdrant client: %s", str(exc))
            raise ExternalServiceError("Qdrant", str(exc)) from exc
    return _qdrant_client


class QdrantVectorClient:
    """Thin wrapper for Qdrant vector storage and similarity searches."""

    def __init__(self, client=None) -> None:
        self.client = client or get_qdrant_client()
        self.collection_name = settings.QDRANT_COLLECTION_NAME

    def _sync_ensure_collection(self) -> None:
        """Create the target collection if it does not already exist."""
        from qdrant_client.models import Distance, VectorParams

        collections = [col.name for col in self.client.get_collections().collections]
        if self.collection_name not in collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_DIMENSION,
                    distance=Distance.COSINE,
                ),
            )
            logger.info("Created Qdrant collection: %s", self.collection_name)

    async def ensure_collection_exists(self) -> None:
        """Asynchronously ensure the vector collection exists in Qdrant."""
        await run_in_threadpool(self._sync_ensure_collection)

    def _sync_upsert_chunks(self, points: List[Any]) -> None:
        """Synchronous point upsert worker."""
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

    async def upsert_chunks(self, points: List[Any]) -> None:
        """Asynchronously upsert chunk vector points into Qdrant."""
        try:
            await run_in_threadpool(self._sync_upsert_chunks, points)
        except Exception as exc:
            logger.error("Qdrant upsert failed: %s", str(exc))
            raise ExternalServiceError("Qdrant Upsert", str(exc)) from exc

    def _sync_search(
        self,
        query_vector: List[float],
        document_ids: Optional[List[str]] = None,
        limit: int = 5,
    ) -> List[Any]:
        """Synchronous similarity search worker with document scope filtering."""
        from qdrant_client.models import FieldCondition, Filter, MatchAny

        search_filter = None
        if document_ids:
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchAny(any=document_ids),
                    )
                ]
            )

        return self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=search_filter,
            limit=limit,
        )

    async def search(
        self,
        query_vector: List[float],
        document_ids: Optional[List[str]] = None,
        limit: int = 5,
    ) -> List[Any]:
        """Perform semantic vector similarity search against Qdrant."""
        try:
            return await run_in_threadpool(
                self._sync_search, query_vector, document_ids, limit
            )
        except Exception as exc:
            logger.error("Qdrant search failed: %s", str(exc))
            raise ExternalServiceError("Qdrant Search", str(exc)) from exc

    def _sync_delete_by_document(self, document_id: str) -> None:
        """Synchronously delete all vector points belonging to a document."""
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id),
                    )
                ]
            ),
        )

    async def delete_by_document_id(self, document_id: str) -> None:
        """Delete all vectors for a specific document from Qdrant."""
        try:
            await run_in_threadpool(self._sync_delete_by_document, document_id)
        except Exception as exc:
            logger.error("Failed to delete vectors for document %s: %s", document_id, str(exc))
            raise ExternalServiceError("Qdrant Delete", str(exc)) from exc
