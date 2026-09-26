"""Pure database access repository for asynchronous document processing jobs."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from starlette.concurrency import run_in_threadpool

from app.core.constants import DocumentStatus, ProcessingStage
from app.integrations.supabase_client import get_supabase_client


class JobRepository:
    """Repository handling CRUD database interactions for processing_jobs."""

    def __init__(self, supabase=None) -> None:
        self.supabase = supabase or get_supabase_client()

    def _sync_create_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        res = self.supabase.table("processing_jobs").insert(job_data).execute()
        return res.data[0] if res.data else {}

    async def create_job(
        self,
        document_id: str,
        status: str = DocumentStatus.UPLOADED.value,
        progress: int = 0,
        current_stage: str = ProcessingStage.UPLOADED.value,
    ) -> Dict[str, Any]:
        """Create a new tracking job for document processing."""
        now = datetime.now(timezone.utc).isoformat()
        job_data = {
            "document_id": document_id,
            "status": status,
            "progress": progress,
            "current_stage": current_stage,
            "error_message": None,
            "created_at": now,
            "updated_at": now,
        }
        return await run_in_threadpool(self._sync_create_job, job_data)

    def _sync_get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        res = self.supabase.table("processing_jobs").select("*").eq("id", job_id).execute()
        return res.data[0] if res.data else None

    async def get_job_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a processing job record by its UUID."""
        return await run_in_threadpool(self._sync_get_job, job_id)

    def _sync_get_latest_job(self, document_id: str) -> Optional[Dict[str, Any]]:
        res = (
            self.supabase.table("processing_jobs")
            .select("*")
            .eq("document_id", document_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    async def get_latest_job_by_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the most recent processing job for a specific document."""
        return await run_in_threadpool(self._sync_get_latest_job, document_id)

    def _sync_update_job(
        self,
        job_id: str,
        status: str,
        progress: int,
        current_stage: str,
        error_message: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        updates = {
            "status": status,
            "progress": progress,
            "current_stage": current_stage,
            "error_message": error_message,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        res = self.supabase.table("processing_jobs").update(updates).eq("id", job_id).execute()
        return res.data[0] if res.data else None

    async def update_job_progress(
        self,
        job_id: str,
        status: str,
        progress: int,
        current_stage: str,
        error_message: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update job stage, progress percentage, and error message."""
        return await run_in_threadpool(
            self._sync_update_job,
            job_id,
            status,
            progress,
            current_stage,
            error_message,
        )
