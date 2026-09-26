"""Pure database access repository for documents and document pages."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from starlette.concurrency import run_in_threadpool

from app.integrations.supabase_client import get_supabase_client


class DocumentRepository:
    """Repository handling CRUD database interactions for documents and pages."""

    def __init__(self, supabase=None) -> None:
        self.supabase = supabase or get_supabase_client()

    def _sync_create_document(self, doc_data: Dict[str, Any]) -> Dict[str, Any]:
        res = self.supabase.table("documents").insert(doc_data).execute()
        return res.data[0] if res.data else {}

    async def create_document(
        self,
        user_id: str,
        filename: str,
        file_type: str,
        file_size: int,
        storage_path: Optional[str] = None,
        status: str = "UPLOADED",
    ) -> Dict[str, Any]:
        """Insert a new document record into the documents table."""
        doc_data = {
            "user_id": user_id,
            "filename": filename,
            "file_type": file_type,
            "file_size": file_size,
            "storage_path": storage_path,
            "status": status,
            "total_pages": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return await run_in_threadpool(self._sync_create_document, doc_data)

    def _sync_get_document(self, document_id: str, user_id: Optional[str]) -> Optional[Dict[str, Any]]:
        query = self.supabase.table("documents").select("*").eq("id", document_id)
        if user_id:
            query = query.eq("user_id", user_id)
        res = query.execute()
        return res.data[0] if res.data else None

    async def get_document_by_id(
        self,
        document_id: str,
        user_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Fetch a single document by its UUID, optionally filtering by owner user_id."""
        return await run_in_threadpool(self._sync_get_document, document_id, user_id)

    def _sync_list_documents(self, user_id: str, limit: int, offset: int) -> Tuple[List[Dict[str, Any]], int]:
        res = (
            self.supabase.table("documents")
            .select("*", count="exact")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        total = res.count if res.count is not None else len(res.data)
        return res.data, total

    async def list_documents(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Fetch a paginated list of documents belonging to a user."""
        return await run_in_threadpool(self._sync_list_documents, user_id, limit, offset)

    def _sync_update_document_status(
        self,
        document_id: str,
        status: str,
        total_pages: Optional[int],
        processed_at: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        updates: Dict[str, Any] = {"status": status}
        if total_pages is not None:
            updates["total_pages"] = total_pages
        if processed_at is not None:
            updates["processed_at"] = processed_at

        res = self.supabase.table("documents").update(updates).eq("id", document_id).execute()
        return res.data[0] if res.data else None

    async def update_document_status(
        self,
        document_id: str,
        status: str,
        total_pages: Optional[int] = None,
        processed_at: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update the overall processing status and page count of a document."""
        return await run_in_threadpool(
            self._sync_update_document_status,
            document_id,
            status,
            total_pages,
            processed_at,
        )

    def _sync_delete_document(self, document_id: str, user_id: str) -> bool:
        res = (
            self.supabase.table("documents")
            .delete()
            .eq("id", document_id)
            .eq("user_id", user_id)
            .execute()
        )
        return bool(res.data)

    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete a document record matching the ID and owner user_id."""
        return await run_in_threadpool(self._sync_delete_document, document_id, user_id)

    # Page-level methods
    def _sync_create_or_update_page(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        # Check if page exists
        existing = (
            self.supabase.table("document_pages")
            .select("id")
            .eq("document_id", page_data["document_id"])
            .eq("page_number", page_data["page_number"])
            .execute()
        )
        if existing.data:
            page_id = existing.data[0]["id"]
            res = self.supabase.table("document_pages").update(page_data).eq("id", page_id).execute()
            return res.data[0] if res.data else {}
        else:
            res = self.supabase.table("document_pages").insert(page_data).execute()
            return res.data[0] if res.data else {}

    async def create_or_update_page(
        self,
        document_id: str,
        page_number: int,
        raw_text: str,
        ocr_used: bool,
        ocr_engine: str,
        language: Optional[str],
        page_status: str,
    ) -> Dict[str, Any]:
        """Insert or update a document page record."""
        page_data = {
            "document_id": document_id,
            "page_number": page_number,
            "raw_text": raw_text,
            "ocr_used": ocr_used,
            "ocr_engine": ocr_engine,
            "language": language,
            "page_status": page_status,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return await run_in_threadpool(self._sync_create_or_update_page, page_data)

    def _sync_get_pages(self, document_id: str) -> List[Dict[str, Any]]:
        res = (
            self.supabase.table("document_pages")
            .select("*")
            .eq("document_id", document_id)
            .order("page_number", desc=False)
            .execute()
        )
        return res.data or []

    async def get_pages_by_document(self, document_id: str) -> List[Dict[str, Any]]:
        """Fetch all pages associated with a document ordered by page number."""
        return await run_in_threadpool(self._sync_get_pages, document_id)

    def _sync_get_page_by_number(self, document_id: str, page_number: int) -> Optional[Dict[str, Any]]:
        res = (
            self.supabase.table("document_pages")
            .select("*")
            .eq("document_id", document_id)
            .eq("page_number", page_number)
            .execute()
        )
        return res.data[0] if res.data else None

    async def get_page_by_number(self, document_id: str, page_number: int) -> Optional[Dict[str, Any]]:
        """Fetch a specific page of a document by page number."""
        return await run_in_threadpool(self._sync_get_page_by_number, document_id, page_number)
