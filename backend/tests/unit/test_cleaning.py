"""Unit tests for text cleaning and normalization stage."""

import pytest
from app.services.pipeline.cleaning import TextCleaner


def test_text_cleaner_removes_control_characters() -> None:
    """Verify that non-printable control characters are stripped."""
    cleaner = TextCleaner()
    dirty_text = "Clean\x00 text\x07 with\x1f artifacts"
    cleaned = cleaner.clean(dirty_text)
    assert cleaned == "Clean text with artifacts"


def test_text_cleaner_normalizes_whitespace_and_newlines() -> None:
    """Verify that redundant newlines and horizontal whitespace are normalized."""
    cleaner = TextCleaner()
    messy_text = "Heading\r\n\r\n\r\n\r\nParagraph with    extra   spaces.\r\n"
    cleaned = cleaner.clean(messy_text)
    assert cleaned == "Heading\n\nParagraph with extra spaces."


def test_text_cleaner_handles_empty_input() -> None:
    """Verify that empty or whitespace-only strings return an empty string."""
    cleaner = TextCleaner()
    assert cleaner.clean("") == ""
    assert cleaner.clean("   \n\t  ") == ""
