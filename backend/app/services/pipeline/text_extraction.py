"""Native PDF text extraction and scanned page detection using PyMuPDF."""

from dataclasses import dataclass
from typing import List, Optional
from starlette.concurrency import run_in_threadpool

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ExtractedPage:
    """Represents text and metadata extracted from a single document page."""

    page_number: int
    raw_text: str
    is_scanned: bool
    image_bytes: Optional[bytes] = None


class PDFTextExtractor:
    """Extracts native text and identifies scanned pages from PDF documents."""

    def __init__(self, min_char_threshold: int = 40) -> None:
        self.min_char_threshold = min_char_threshold

    def _sync_extract(self, pdf_bytes: bytes) -> List[ExtractedPage]:
        """Synchronous PDF page extraction worker using PyMuPDF."""
        import fitz  # PyMuPDF

        pages: List[ExtractedPage] = []
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        try:
            for page_index in range(len(doc)):
                page_num = page_index + 1
                page = doc.load_page(page_index)
                text = page.get_text("text").strip()

                # If text is below minimal character threshold, classify page as scanned
                is_scanned = len(text) < self.min_char_threshold
                img_bytes: Optional[bytes] = None

                if is_scanned:
                    # Render page to PNG pixmap for OCR processing
                    pix = page.get_pixmap(dpi=150)
                    img_bytes = pix.tobytes("png")

                pages.append(
                    ExtractedPage(
                        page_number=page_num,
                        raw_text=text,
                        is_scanned=is_scanned,
                        image_bytes=img_bytes,
                    )
                )
        finally:
            doc.close()

        return pages

    async def extract_pages(self, pdf_bytes: bytes) -> List[ExtractedPage]:
        """Asynchronously extract native text and identify scanned pages in PDF."""
        return await run_in_threadpool(self._sync_extract, pdf_bytes)
