"""System constants and enumerations for the document intelligence platform."""

from enum import Enum


class DocumentStatus(str, Enum):
    """Lifecycle status of a document."""
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class PageStatus(str, Enum):
    """Processing status of an individual document page."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class InputMode(str, Enum):
    """Modality of a user message."""
    TEXT = "text"
    VOICE = "voice"


class MessageRole(str, Enum):
    """Conversation message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class OCREngine(str, Enum):
    """OCR engine applied to a page."""
    NONE = "none"
    PADDLE_OCR = "paddle_ocr"
    SARVAM_VISION = "sarvam_vision"


class ProcessingStage(str, Enum):
    """Current stage of the document processing pipeline."""
    UPLOADED = "Uploaded"
    DETECTING_TYPE = "Detecting document type"
    EXTRACTING_TEXT = "Extracting native text"
    OCR_PROCESSING = "Running OCR"
    EXTRACTING_TABLES = "Extracting tables"
    CLEANING = "Cleaning and structure detection"
    CHUNKING = "Chunking document"
    GENERATING_EMBEDDINGS = "Generating embeddings"
    INDEXING = "Indexing vectors"
    COMPLETED = "Completed"
    FAILED = "Failed"


class SupportedFileType(str, Enum):
    """Supported input document file extensions."""
    PDF = "pdf"
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    DOCX = "docx"
    TXT = "txt"
    CSV = "csv"
