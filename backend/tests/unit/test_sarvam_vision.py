"""Unit tests for Sarvam Vision Indic OCR and 10-page batching."""

from unittest.mock import AsyncMock, MagicMock, patch
import fitz
import pytest

from app.integrations.sarvam.vision_client import SarvamVisionClient
from app.services.pipeline.ocr_indic import IndicOCRPipeline


def create_multi_page_pdf(num_pages: int = 15) -> bytes:
    """Helper to generate a multi-page PDF."""
    doc = fitz.open()
    for i in range(num_pages):
        page = doc.new_page()
        page.insert_text((50, 72), f"Page {i + 1} content")
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


@pytest.mark.asyncio
async def test_indic_ocr_batching_and_stitching() -> None:
    """Verify that a 15-page document is split into 10-page batches and re-stitched."""
    pdf_bytes = create_multi_page_pdf(15)

    mock_vision = AsyncMock()
    # Batch 1 (1-10)
    mock_vision.digitize_document.side_effect = [
        {"pages": [{"text": f"Digitized page {i}", "confidence": 0.98} for i in range(1, 11)]},
        {"pages": [{"text": f"Digitized page {i}", "confidence": 0.98} for i in range(11, 16)]},
    ]

    pipeline = IndicOCRPipeline(vision_client=mock_vision)
    results = await pipeline.process_document_pages(pdf_bytes, language_tag="hi-IN")

    assert len(results) == 15
    assert results[0]["page_number"] == 1
    assert results[14]["page_number"] == 15
    assert mock_vision.digitize_document.call_count == 2


@pytest.mark.asyncio
async def test_indic_ocr_fallback_to_paddle_on_failure() -> None:
    """Verify that if Sarvam Vision fails, pipeline falls back to PaddleOCR."""
    pdf_bytes = create_multi_page_pdf(2)

    mock_vision = AsyncMock()
    mock_vision.digitize_document.side_effect = Exception("Sarvam Vision timeout")

    mock_fallback_ocr = AsyncMock()
    from app.integrations.ocr.base import OCRExtractionResult
    mock_fallback_ocr.extract_text_from_image.return_value = OCRExtractionResult(
        text="Fallback extracted text",
        confidence=0.5,
        engine_name="paddle_ocr",
    )

    pipeline = IndicOCRPipeline(vision_client=mock_vision, fallback_ocr=mock_fallback_ocr)
    results = await pipeline.process_document_pages(pdf_bytes, language_tag="hi-IN")

    assert len(results) == 2
    assert results[0]["ocr_engine"] == "paddle_ocr_fallback"
    assert results[0]["confidence"] == 0.5
