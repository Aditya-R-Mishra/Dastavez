"""Text normalization and extraction artifact cleaning pipeline stage."""

import re


class TextCleaner:
    """Cleans extracted document text by removing artifacts while preserving structure."""

    def clean(self, raw_text: str) -> str:
        """Normalize line breaks, clean redundant whitespace, and strip control artifacts."""
        if not raw_text:
            return ""

        # Remove control characters except standard whitespace (newlines, tabs)
        cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", raw_text)

        # Normalize line endings to standard \n
        cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")

        # Replace excessive spaces or horizontal tabs while preserving line structure
        cleaned = re.sub(r"[ \t]+", " ", cleaned)

        # Strip spaces from line start and end
        lines = [line.strip() for line in cleaned.split("\n")]

        # Collapse more than two consecutive empty lines down to one
        normalized_lines = []
        consecutive_empty = 0
        for line in lines:
            if not line:
                consecutive_empty += 1
                if consecutive_empty <= 1:
                    normalized_lines.append("")
            else:
                consecutive_empty = 0
                normalized_lines.append(line)

        return "\n".join(normalized_lines).strip()
