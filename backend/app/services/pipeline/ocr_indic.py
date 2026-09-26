"""Indic-language OCR pipeline using Sarvam Vision with batching, stitching, and fallback."""

from typing import Any, Dict, List, Optional, Tuple
import fitz  # PyMuPDF
from starlette.concurrency import run_in_threadpool

from app.core.logging import get_logger
from app.integrations.ocr.base import BaseOCREngine
from app.integrations.ocr.paddle_ocr import PaddleOCREngine
from app.integrations.sarvam.vision_client import SarvamVisionClient

logger = get_logger(__name__)


class IndicOCRPipeline:
    """Orchestrates Sarvam Vision OCR on Indic-script documents with 10-page batching."""

    def __init__(
        self,
        vision_client: Optional[SarvamVisionClient] = None,
        fallback_ocr: Optional[BaseOCREngine] = None,
    ) -> None:
        self.vision_client = vision_client or SarvamVisionClient()
        self.fallback_ocr = fallback_ocr or PaddleOCREngine()

    def _split_into_10page_batches(self, pdf_bytes: bytes, batch_size: int = 10) -> List[Tuple[int, int, bytes]]:
        """Split a multi-page PDF into batches of <= 10 pages for Sarvam Vision limits."""
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_pages = len(doc)
        batches: List[Tuple[int, int, bytes]] = []

        for start in range(0, total_pages, batch_size):
            end = min(start + batch_size, total_pages)
            batch_doc = fitz.open()
            batch_doc.insert_pdf(doc, from_page=start, to_page=end - 1)
            batch_bytes = batch_doc.tobytes()
            batch_doc.close()
            batches.append((start + 1, end, batch_bytes))

        doc.close()
        return batches

    async def process_document_pages(
        self,
        pdf_bytes: bytes,
        language_tag: Optional[str] = "hi-IN",
    ) -> List[Dict[str, Any]]:
        """Process document through Sarvam Vision with batching and PaddleOCR fallback."""
        batches = await run_in_threadpool(self._split_into_10page_batches, pdf_bytes, 10)
        stitched_pages: List[Dict[str, Any]] = []

        for start_page, end_page, batch_bytes in batches:
            try:
                logger.info(
                    "Submitting pages %d-%d to Sarvam Vision (language: %s)",
                    start_page,
                    end_page,
                    language_tag,
                )
                result = await self.vision_client.digitize_document(
                    file_bytes=batch_bytes,
                    filename=f"batch_{start_page}_{end_page}.pdf",
                    language_code=language_tag,
                )

                # Parse Sarvam Vision page output
                pages_data = result.get("pages", [])
                if pages_data:
                    for idx, page_item in enumerate(pages_data):
                        actual_page_num = start_page + idx
                        stitched_pages.append({
                            "page_number": actual_page_num,
                            "raw_text": page_item.get("content", page_item.get("text", "")),
                            "ocr_used": True,
                            "ocr_engine": "sarvam_vision",
                            "confidence": float(page_item.get("confidence", 0.95)),
                            "language": language_tag,
                        })
                else:
                    # Single full text response fallback
                    full_text = result.get("content", result.get("text", ""))
                    stitched_pages.append({
                        "page_number": start_page,
                        "raw_text": full_text,
                        "ocr_used": True,
                        "ocr_engine": "sarvam_vision",
                        "confidence": 0.9,
                        "language": language_tag,
                    })

            except Exception as exc:
                logger.warning(
                    "Sarvam Vision failed for pages %d-%d: %s; falling back to PaddleOCR",
                    start_page,
                    end_page,
                    str(exc),
                )
                # Fallback to local PaddleOCR per page
                batch_doc = fitz.open(stream=batch_bytes, filetype="pdf")
                for page_idx in range(len(batch_doc)):
                    actual_page_num = start_page + page_idx
                    page = batch_doc.load_page(page_idx)
                    pix = page.get_pixmap(dpi=150)
                    img_bytes = pix.tobytes("png")

                    ocr_res = await self.fallback_ocr.extract_text_from_image(img_bytes)
                    stitched_pages.append({
                        "page_number": actual_page_num,
                        "raw_text": ocr_res.text,
                        "ocr_used": True,
                        "ocr_engine": "paddle_ocr_fallback",
                        "confidence": 0.5,  # Low confidence flag per PRD
                        "language": language_tag,
                    })
                batch_doc.close()

        return stitched_pages
