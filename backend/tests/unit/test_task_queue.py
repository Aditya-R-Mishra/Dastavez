"""Unit tests for task queue dispatching (Celery and FastAPI BackgroundTasks)."""

from unittest.mock import MagicMock, patch
from fastapi import BackgroundTasks

from app.workers.task_queue import dispatch_processing_task


def test_dispatch_processing_task_in_process_fallback() -> None:
    """Verify dispatch_processing_task adds task to BackgroundTasks when USE_CELERY is False."""
    mock_bg = MagicMock(spec=BackgroundTasks)

    with patch("app.workers.task_queue.settings.USE_CELERY", False):
        dispatch_processing_task(
            background_tasks=mock_bg,
            job_id="job-1",
            document_id="doc-1",
            user_id="user-1",
        )

    mock_bg.add_task.assert_called_once()


def test_dispatch_processing_task_celery_when_enabled() -> None:
    """Verify dispatch_processing_task dispatches to Celery delay() when USE_CELERY is True."""
    mock_bg = MagicMock(spec=BackgroundTasks)
    mock_task = MagicMock()

    with patch("app.workers.task_queue.settings.USE_CELERY", True):
        with patch("app.workers.celery_app.process_document_celery_task.delay", mock_task):
            dispatch_processing_task(
                background_tasks=mock_bg,
                job_id="job-2",
                document_id="doc-2",
                user_id="user-2",
            )

    mock_task.assert_called_once_with(job_id="job-2", document_id="doc-2", user_id="user-2")
    mock_bg.add_task.assert_not_called()
