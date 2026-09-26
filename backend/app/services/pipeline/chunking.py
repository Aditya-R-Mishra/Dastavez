"""Section-aware document text chunker with configurable token window and overlap."""

import uuid
from typing import Any, Dict, List, Optional

from app.core.config import settings


class DocumentChunker:
    """Chunks cleaned document text while preserving section boundaries and metadata."""

    def __init__(
        self,
        chunk_size_tokens: Optional[int] = None,
        chunk_overlap_tokens: Optional[int] = None,
    ) -> None:
        self.chunk_size = chunk_size_tokens or settings.CHUNK_SIZE_TOKENS
        self.overlap = chunk_overlap_tokens or settings.CHUNK_OVERLAP_TOKENS

    def _estimate_tokens(self, text: str) -> int:
        """Rough token count approximation based on words and whitespace (~1.3 tokens per word)."""
        words = text.split()
        return max(1, int(len(words) * 1.3))

    def chunk_page(
        self,
        document_id: str,
        page_id: str,
        page_number: int,
        text: str,
        start_chunk_index: int = 0,
        filename: Optional[str] = None,
        language: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Split page text into overlapping semantic chunks with full attribution metadata."""
        if not text.strip():
            return []

        # Split paragraphs on double newlines to preserve structural integrity
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if not paragraphs:
            paragraphs = [text.strip()]

        chunks: List[Dict[str, Any]] = []
        current_paragraphs: List[str] = []
        current_token_count = 0
        current_section = ""
        current_index = start_chunk_index

        for para in paragraphs:
            # Check if paragraph looks like a heading
            if para.startswith("#") or (len(para) < 60 and "\n" not in para and para.isupper()):
                current_section = para.lstrip("#").strip()

            para_tokens = self._estimate_tokens(para)

            if current_token_count + para_tokens > self.chunk_size and current_paragraphs:
                # Flush existing chunk
                chunk_content = "\n\n".join(current_paragraphs)
                chunk_uuid = str(uuid.uuid4())
                chunks.append({
                    "chunk_id": chunk_uuid,
                    "document_id": document_id,
                    "page_id": page_id,
                    "page_number": page_number,
                    "chunk_index": current_index,
                    "content": chunk_content,
                    "language": language,
                    "metadata": {
                        "chunk_id": chunk_uuid,
                        "document_id": document_id,
                        "page": page_number,
                        "filename": filename or "",
                        "section": current_section,
                        "content": chunk_content,
                        "language": language or "en",
                    },
                })
                current_index += 1

                # Retain overlap from previous paragraph if possible
                if current_paragraphs:
                    current_paragraphs = [current_paragraphs[-1]]
                    current_token_count = self._estimate_tokens(current_paragraphs[0])
                else:
                    current_paragraphs = []
                    current_token_count = 0

            current_paragraphs.append(para)
            current_token_count += para_tokens

        # Flush any remaining paragraphs
        if current_paragraphs:
            chunk_content = "\n\n".join(current_paragraphs)
            chunk_uuid = str(uuid.uuid4())
            chunks.append({
                "chunk_id": chunk_uuid,
                "document_id": document_id,
                "page_id": page_id,
                "page_number": page_number,
                "chunk_index": current_index,
                "content": chunk_content,
                "language": language,
                "metadata": {
                    "chunk_id": chunk_uuid,
                    "document_id": document_id,
                    "page": page_number,
                    "filename": filename or "",
                    "section": current_section,
                    "content": chunk_content,
                    "language": language or "en",
                },
            })

        return chunks
