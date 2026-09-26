"""Latin-script OCR extraction pipeline stage using BaseOCREngine."""

from typing import Optional
from app.integrations.ocr.base import BaseOCREngine, OCRExtractionResult
from app.integrations.ocr.paddle_ocr import PaddleOCREngine


class LatinOCRPipeline:
    """Orchestrates Latin-script OCR execution on scanned pages and images."""

    def __init__(self, ocr_engine: Optional[BaseOCREngine] = None) -> None:
        self.ocr_engine = ocr_engine or PaddleOCREngine()

    async def process_image(
        self,
        image_bytes: bytes,
        language_hint: Optional[str] = "en",
    ) -> OCRExtractionResult:
        """Run Latin OCR on image bytes and return normalized extraction results."""
        return await self.ocr_engine.extract_text_from_image(
            image_bytes=image_bytes,
            language_hint=language_hint,
        )
