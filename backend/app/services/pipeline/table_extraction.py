"""Table extraction and structural relationship preservation."""

from typing import List
import fitz  # PyMuPDF
from starlette.concurrency import run_in_threadpool

from app.core.logging import get_logger

logger = get_logger(__name__)


class TableExtractor:
    """Detects tables and converts them to structured Markdown representations."""

    def _sync_extract_tables(self, pdf_bytes: bytes, page_number: int) -> List[str]:
        """Extract tables from a specific PDF page as Markdown strings."""
        tables_markdown: List[str] = []
        doc = None
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            page_index = page_number - 1
            if 0 <= page_index < len(doc):
                page = doc.load_page(page_index)
                tabs = page.find_tables()
                for tab in tabs:
                    # Convert detected table to Markdown format
                    df = tab.to_pandas()
                    if not df.empty:
                        tables_markdown.append(df.to_markdown(index=False))
        except Exception as exc:
            logger.warning("Table extraction error on page %d: %s", page_number, str(exc))
        finally:
            if doc is not None:
                doc.close()

        return tables_markdown

    async def extract_tables(self, pdf_bytes: bytes, page_number: int) -> List[str]:
        """Asynchronously extract structured tables from a PDF page."""
        return await run_in_threadpool(self._sync_extract_tables, pdf_bytes, page_number)
