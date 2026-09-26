"""PaddleOCR integration engine implementing BaseOCREngine."""

import asyncio
from typing import Optional
from starlette.concurrency import run_in_threadpool

from app.core.exceptions import OCRFailedError
from app.core.logging import get_logger
from app.integrations.ocr.base import BaseOCREngine, OCRExtractionResult, OCRTextBlock

logger = get_logger(__name__)


class PaddleOCREngine(BaseOCREngine):
    """PaddleOCR engine for Latin script OCR extraction."""

    def __init__(self, use_angle_cls: bool = True, lang: str = "en") -> None:
        self.lang = lang
        self.use_angle_cls = use_angle_cls
        self._ocr_instance = None

    def _get_ocr_instance(self):
        """Lazy initialization of PaddleOCR instance to minimize startup time."""
        if self._ocr_instance is None:
            try:
                from paddleocr import PaddleOCR
                self._ocr_instance = PaddleOCR(use_angle_cls=self.use_angle_cls, lang=self.lang)
            except ImportError:
                logger.warning("paddleocr library is not installed; running in fallback mode")
                self._ocr_instance = False
        return self._ocr_instance

    def _sync_extract(self, image_bytes: bytes) -> OCRExtractionResult:
        """Synchronous extraction worker executed inside a threadpool."""
        instance = self._get_ocr_instance()
        if not instance:
            # Fallback when PaddleOCR native binaries are not available in current environment
            return OCRExtractionResult(
                text="",
                confidence=0.0,
                blocks=[],
                engine_name="paddle_ocr",
            )

        try:
            import numpy as np
            import cv2
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            result = instance.ocr(img, cls=self.use_angle_cls)
            extracted_lines = []
            blocks = []
            total_conf = 0.0
            count = 0

            if result and result[0]:
                for line in result[0]:
                    box = line[0]
                    text_conf = line[1]
                    text = text_conf[0]
                    conf = float(text_conf[1])
                    extracted_lines.append(text)
                    blocks.append(OCRTextBlock(text=text, confidence=conf, bounding_box=box))
                    total_conf += conf
                    count += 1

            avg_conf = (total_conf / count) if count > 0 else 0.0
            full_text = "\n".join(extracted_lines)
            return OCRExtractionResult(
                text=full_text,
                confidence=avg_conf,
                blocks=blocks,
                engine_name="paddle_ocr",
            )
        except Exception as exc:
            logger.error("PaddleOCR extraction encountered an error: %s", str(exc))
            raise OCRFailedError(page_number=0, reason=str(exc)) from exc

    async def extract_text_from_image(
        self,
        image_bytes: bytes,
        language_hint: Optional[str] = None,
    ) -> OCRExtractionResult:
        """Asynchronously extract text from image bytes using a threadpool."""
        return await run_in_threadpool(self._sync_extract, image_bytes)
