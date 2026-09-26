"""Unit tests for PDF native text extraction using PyMuPDF."""

import fitz  # PyMuPDF
import pytest
from app.services.pipeline.text_extraction import PDFTextExtractor


def create_sample_pdf_bytes(text: str) -> bytes:
    """Helper to generate an in-memory PDF with specified text."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


@pytest.mark.asyncio
async def test_pdf_native_text_extraction() -> None:
    """Verify that PyMuPDF extracts text correctly from a born-digital PDF."""
    content = "This is a native digital document regarding policy guidelines."
    pdf_bytes = create_sample_pdf_bytes(content)

    extractor = PDFTextExtractor(min_char_threshold=10)
    pages = await extractor.extract_pages(pdf_bytes)

    assert len(pages) == 1
    assert pages[0].page_number == 1
    assert "policy guidelines" in pages[0].raw_text
    assert not pages[0].is_scanned


@pytest.mark.asyncio
async def test_pdf_scanned_page_detection() -> None:
    """Verify that a page with little or no text is marked as scanned."""
    doc = fitz.open()
    doc.new_page()  # Blank page
    pdf_bytes = doc.tobytes()
    doc.close()

    extractor = PDFTextExtractor(min_char_threshold=20)
    pages = await extractor.extract_pages(pdf_bytes)

    assert len(pages) == 1
    assert pages[0].is_scanned is True
    assert pages[0].image_bytes is not None
