"""Celery application and task definitions for distributed document ingestion."""

import asyncio
from typing import Any, Dict
from celery import Celery

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

celery_app = Celery(
    "dastavez",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)


@celery_app.task(name="dastavez.process_document", bind=True, max_retries=3)
def process_document_celery_task(
    self: Any,
    job_id: str,
    document_id: str,
    user_id: str,
) -> Dict[str, Any]:
    """Celery background worker task executing document parsing and vectorization."""
    from app.workers.processing_worker import DocumentProcessingWorker

    logger.info("Celery task started for job '%s' (doc: '%s')", job_id, document_id)
    try:
        worker = DocumentProcessingWorker()
        result = asyncio.run(
            worker.process_document(
                job_id=job_id,
                document_id=document_id,
                user_id=user_id,
            )
        )
        logger.info("Celery task finished successfully for job '%s'", job_id)
        return {"status": "SUCCESS", "job_id": job_id, "document_id": document_id, "result": result}
    except Exception as exc:
        logger.error("Celery task error on job '%s': %s", job_id, str(exc))
        raise self.retry(exc=exc, countdown=10)
