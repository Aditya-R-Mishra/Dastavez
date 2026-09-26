"""Unit tests for domain exceptions and status codes."""

import pytest
from app.core.exceptions import (
    AppException,
    AuthenticationError,
    ConflictingInformationError,
    DocumentAccessDeniedError,
    DocumentNotFoundError,
    FileSizeLimitExceededError,
    InsufficientEvidenceError,
    InvalidFileTypeError,
    OCRFailedError,
)


def test_exception_status_codes() -> None:
    """Verify default status and error codes for custom exceptions."""
    exc1 = DocumentNotFoundError("doc-123")
    assert exc1.status_code == 404
    assert exc1.error_code == "DOCUMENT_NOT_FOUND"
    assert exc1.details["document_id"] == "doc-123"

    exc2 = DocumentAccessDeniedError("doc-123")
    assert exc2.status_code == 403
    assert exc2.error_code == "DOCUMENT_ACCESS_DENIED"

    exc3 = InvalidFileTypeError("exe", ["pdf", "docx"])
    assert exc3.status_code == 400
    assert exc3.error_code == "INVALID_FILE_TYPE"

    exc4 = FileSizeLimitExceededError(50000000)
    assert exc4.status_code == 413
    assert exc4.error_code == "FILE_SIZE_EXCEEDED"

    exc5 = OCRFailedError(1, "Corrupted image")
    assert exc5.status_code == 500
    assert exc5.error_code == "OCR_EXTRACTION_FAILED"

    exc6 = InsufficientEvidenceError("What is the clause?")
    assert exc6.status_code == 422
    assert exc6.error_code == "INSUFFICIENT_EVIDENCE"

    exc7 = ConflictingInformationError(["Conflict 1", "Conflict 2"])
    assert exc7.status_code == 422
    assert exc7.error_code == "CONFLICTING_INFORMATION"
