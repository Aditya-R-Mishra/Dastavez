"""Pure database access repository for text chunks."""

from datetime import datetime, timezone
from typing import Any, Dict, List
from starlette.concurrency import run_in_threadpool

from app.integrations.supabase_client import get_supabase_client


class ChunkRepository:
    """Repository handling database operations for the chunks table."""

    def __init__(self, supabase=None) -> None:
        self.supabase = supabase or get_supabase_client()

    def _sync_create_chunks(self, chunks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not chunks_data:
            return []
        now = datetime.now(timezone.utc).isoformat()
        records = []
        for c in chunks_data:
            records.append({
                "document_id": c["document_id"],
                "page_id": c["page_id"],
                "chunk_index": c["chunk_index"],
                "content": c["content"],
                "language": c.get("language"),
                "metadata": c.get("metadata", {}),
                "created_at": now,
            })
        res = self.supabase.table("chunks").insert(records).execute()
        return res.data or []

    async def create_chunks(self, chunks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Batch insert chunk records into the chunks table."""
        return await run_in_threadpool(self._sync_create_chunks, chunks_data)

    def _sync_get_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        res = (
            self.supabase.table("chunks")
            .select("*")
            .eq("document_id", document_id)
            .order("chunk_index", desc=False)
            .execute()
        )
        return res.data or []

    async def get_chunks_by_document(self, document_id: str) -> List[Dict[str, Any]]:
        """Fetch all chunks for a specific document ordered by index."""
        return await run_in_threadpool(self._sync_get_chunks, document_id)

    def _sync_delete_chunks(self, document_id: str) -> bool:
        res = self.supabase.table("chunks").delete().eq("document_id", document_id).execute()
        return bool(res.data)

    async def delete_chunks_by_document(self, document_id: str) -> bool:
        """Delete all chunk records belonging to a document."""
        return await run_in_threadpool(self._sync_delete_chunks, document_id)
