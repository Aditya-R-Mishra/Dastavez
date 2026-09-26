"""Structured logging configuration for the application."""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict


class StructuredJsonFormatter(logging.Formatter):
    """Formats log records as structured JSON dictionaries."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the specified record as a JSON string."""
        log_payload: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include custom contextual tracking fields if present
        for field in ("document_id", "job_id", "user_id", "stage", "page_number"):
            if hasattr(record, field):
                log_payload[field] = getattr(record, field)

        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_payload)


def setup_logging(debug: bool = False) -> None:
    """Initialize structured logging for application root and components."""
    log_level = logging.DEBUG if debug else logging.INFO

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(StructuredJsonFormatter())
    root_logger.addHandler(stream_handler)

    # Set third-party loggers to a reasonable level
    for lib in ("uvicorn.access", "httpx", "httpcore", "postgrest"):
        logging.getLogger(lib).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Retrieve a configured logger by component name."""
    return logging.getLogger(name)
