"""Pipeline router determining optimal extraction strategy per file and page."""

from typing import Optional
from app.core.constants import SupportedFileType


class PipelineRouter:
    """Routes documents and pages to appropriate extraction and OCR engines."""

    @staticmethod
    def get_file_category(file_type: str) -> str:
        """Categorize file extension into extraction pipeline type."""
        clean = file_type.lower().strip(".").strip()
        if clean == SupportedFileType.PDF.value:
            return "pdf"
        elif clean in (SupportedFileType.PNG.value, SupportedFileType.JPG.value, SupportedFileType.JPEG.value):
            return "image"
        elif clean in (SupportedFileType.DOCX.value, SupportedFileType.TXT.value, SupportedFileType.CSV.value):
            return "direct"
        else:
            return "unsupported"

    @staticmethod
    def route_page_extraction(
        is_scanned: bool,
        detected_script: Optional[str] = None,
        language_tag: Optional[str] = None,
    ) -> str:
        """Determine whether a page requires native text, Latin OCR, or Indic OCR."""
        if not is_scanned:
            return "native_text"

        # Check if page is identified as Indian regional script
        indic_scripts = ("devanagari", "bengali", "tamil", "telugu", "gujarati", "kannada", "malayalam", "gurmukhi", "odia")
        if detected_script and detected_script.lower() in indic_scripts:
            return "ocr_indic"

        if language_tag and any(tag in language_tag.lower() for tag in ("hi", "mr", "ta", "te", "bn", "gu", "kn", "ml")):
            return "ocr_indic"

        return "ocr_latin"
