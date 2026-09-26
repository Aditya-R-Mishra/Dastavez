"""Application exception definitions and unified FastAPI exception handlers."""

import logging
from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base exception class for all domain and application errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_SERVER_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


class AuthenticationError(AppException):
    """Raised when authentication credentials are invalid or missing."""

    def __init__(self, message: str = "Invalid or expired authentication credentials") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_FAILED",
        )


class PermissionDeniedError(AppException):
    """Raised when an authenticated user attempts to access an unauthorized resource."""

    def __init__(self, message: str = "Permission denied for this resource") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="PERMISSION_DENIED",
        )


class DocumentNotFoundError(AppException):
    """Raised when a requested document ID does not exist."""

    def __init__(self, document_id: str) -> None:
        super().__init__(
            message=f"Document '{document_id}' was not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="DOCUMENT_NOT_FOUND",
            details={"document_id": document_id},
        )


class DocumentAccessDeniedError(AppException):
    """Raised when a user attempts to access a document belonging to another user."""

    def __init__(self, document_id: str) -> None:
        super().__init__(
            message=f"Access to document '{document_id}' is denied",
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="DOCUMENT_ACCESS_DENIED",
            details={"document_id": document_id},
        )


class InvalidFileTypeError(AppException):
    """Raised when an uploaded document file extension or MIME type is unsupported."""

    def __init__(self, file_type: str, allowed_types: Optional[list] = None) -> None:
        super().__init__(
            message=f"File type '{file_type}' is not supported. Allowed: {allowed_types}",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_FILE_TYPE",
            details={"file_type": file_type, "allowed_types": allowed_types},
        )


class FileSizeLimitExceededError(AppException):
    """Raised when an uploaded document exceeds the configured maximum file size."""

    def __init__(self, max_size_bytes: int) -> None:
        super().__init__(
            message=f"File size exceeds maximum allowed limit of {max_size_bytes} bytes",
            status_code=getattr(status, "HTTP_413_CONTENT_TOO_LARGE", 413),
            error_code="FILE_SIZE_EXCEEDED",
            details={"max_size_bytes": max_size_bytes},
        )


class ProcessingJobNotFoundError(AppException):
    """Raised when a processing job status query references an unknown job ID."""

    def __init__(self, job_id: str) -> None:
        super().__init__(
            message=f"Processing job '{job_id}' was not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="JOB_NOT_FOUND",
            details={"job_id": job_id},
        )


class OCRFailedError(AppException):
    """Raised when an OCR engine fails to extract text from a page or image."""

    def __init__(self, page_number: int, reason: str) -> None:
        super().__init__(
            message=f"OCR failed for page {page_number}: {reason}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="OCR_EXTRACTION_FAILED",
            details={"page_number": page_number, "reason": reason},
        )


class InsufficientEvidenceError(AppException):
    """Raised when retrieved chunks do not contain enough evidence to ground an answer."""

    def __init__(self, query: str, missing_info: Optional[str] = None) -> None:
        super().__init__(
            message="Insufficient evidence found in uploaded documents to answer this query",
            status_code=getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422),
            error_code="INSUFFICIENT_EVIDENCE",
            details={"query": query, "missing_info": missing_info},
        )


class ConflictingInformationError(AppException):
    """Raised when conflicting evidence across sources cannot be reconciled."""

    def __init__(self, conflicts: list) -> None:
        super().__init__(
            message="Uploaded documents contain conflicting evidence for the specified query",
            status_code=getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422),
            error_code="CONFLICTING_INFORMATION",
            details={"conflicts": conflicts},
        )


class ExternalServiceError(AppException):
    """Raised when an external API (Supabase, Sarvam, Qdrant, LLM) call fails."""

    def __init__(self, service_name: str, reason: str) -> None:
        super().__init__(
            message=f"External service '{service_name}' failed: {reason}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service_name": service_name, "reason": reason},
        )


class FeatureNotImplementedError(AppException):
    """Raised explicitly when an endpoint or feature is scoped for future phases."""

    def __init__(self, feature_name: str) -> None:
        super().__init__(
            message=f"Feature '{feature_name}' is not yet implemented",
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            error_code="NOT_IMPLEMENTED",
            details={"feature": feature_name},
        )


async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    """Map domain AppException instances to standard structured JSON responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
        },
    )


async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    """Map request validation errors to standard structured JSON responses."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "message": "Invalid request parameters or payload",
            "details": {"errors": exc.errors()},
        },
    )


async def not_implemented_handler(_: Request, exc: NotImplementedError) -> JSONResponse:
    """Map standard NotImplementedError to standard 501 HTTP response."""
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={
            "success": False,
            "error_code": "NOT_IMPLEMENTED",
            "message": str(exc) or "Requested feature is not yet implemented",
            "details": {},
        },
    )


async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unexpected internal server errors."""
    logger.exception("Unhandled server exception: %s", str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected internal error occurred",
            "details": {},
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI application instance."""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(NotImplementedError, not_implemented_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
