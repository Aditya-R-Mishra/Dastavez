"""Unified task dispatch abstraction supporting Celery or FastAPI BackgroundTasks."""

from fastapi import BackgroundTasks

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def dispatch_processing_task(
    background_tasks: BackgroundTasks,
    job_id: str,
    document_id: str,
    user_id: str,
) -> None:
    """Dispatch document processing job via Celery worker or FastAPI background task."""
    if settings.USE_CELERY:
        try:
            from app.workers.celery_app import process_document_celery_task

            logger.info("Enqueuing job '%s' to Celery broker (%s)", job_id, settings.REDIS_URL)
            process_document_celery_task.delay(
                job_id=job_id,
                document_id=document_id,
                user_id=user_id,
            )
            return
        except Exception as exc:
            logger.warning(
                "Celery task dispatch failed (%s), falling back to in-process background task: %s",
                settings.REDIS_URL,
                str(exc),
            )

    # In-process execution fallback via FastAPI BackgroundTasks
    from app.workers.processing_worker import run_document_pipeline_task

    background_tasks.add_task(
        run_document_pipeline_task,
        document_id=document_id,
        job_id=job_id,
        user_id=user_id,
    )
    logger.info("Dispatched job '%s' to in-process background worker", job_id)
