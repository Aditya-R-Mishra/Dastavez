"""Unit tests for PDF table extraction service."""

from unittest.mock import MagicMock, patch
import fitz
import pytest

from app.services.pipeline.table_extraction import TableExtractor


@pytest.mark.asyncio
async def test_table_extractor_extracts_markdown_table() -> None:
    """Verify TableExtractor detects tables and returns markdown representations."""
    extractor = TableExtractor()

    # Create a simple PDF in memory
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Sample Table Page")
    pdf_bytes = doc.tobytes()
    doc.close()

    mock_tab = MagicMock()
    mock_df = MagicMock()
    mock_df.empty = False
    mock_df.to_markdown.return_value = "| Col1 | Col2 |\n| --- | --- |\n| Val1 | Val2 |"
    mock_tab.to_pandas.return_value = mock_df

    mock_tabs = MagicMock()
    mock_tabs.__iter__.return_value = [mock_tab]

    with patch.object(fitz.Page, "find_tables", return_value=mock_tabs):
        tables = await extractor.extract_tables(pdf_bytes, page_number=1)

    assert len(tables) == 1
    assert "| Col1 | Col2 |" in tables[0]


@pytest.mark.asyncio
async def test_table_extractor_handles_empty_or_error() -> None:
    """Verify TableExtractor returns empty list gracefully on invalid input."""
    extractor = TableExtractor()
    tables = await extractor.extract_tables(b"not-a-valid-pdf", page_number=1)
    assert tables == []
