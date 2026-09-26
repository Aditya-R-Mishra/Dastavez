"""Base interface and data structures for OCR extraction engines."""

from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, Field


class OCRTextBlock(BaseModel):
    """Individual recognized text block with bounding box and confidence."""

    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    bounding_box: Optional[List[List[float]]] = None


class OCRExtractionResult(BaseModel):
    """Unified result payload produced by an OCR engine."""

    text: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    blocks: List[OCRTextBlock] = Field(default_factory=list)
    engine_name: str
    detected_language: Optional[str] = None


class BaseOCREngine(ABC):
    """Abstract base class for all OCR engine integrations."""

    @abstractmethod
    async def extract_text_from_image(
        self,
        image_bytes: bytes,
        language_hint: Optional[str] = None,
    ) -> OCRExtractionResult:
        """Extract text from raw image bytes asynchronously."""
        pass
