"""Unit tests for Sarvam Mayura Translation client."""

from unittest.mock import AsyncMock, patch
import httpx
import pytest

from app.core.exceptions import ExternalServiceError
from app.integrations.sarvam.mayura_client import SarvamMayuraClient


@pytest.mark.asyncio
async def test_mayura_translation_success() -> None:
    """Verify Mayura client translates text and extracts translated_text."""
    client = SarvamMayuraClient(api_key="test-key", base_url="https://api.sarvam.ai")

    mock_resp = AsyncMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"translated_text": "यह एक दस्तावेज़ है।"}

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        translated = await client.translate_text(
            text="This is a document.",
            source_language_code="en-IN",
            target_language_code="hi-IN",
        )

    assert translated == "यह एक दस्तावेज़ है।"


@pytest.mark.asyncio
async def test_mayura_translation_error() -> None:
    """Verify Mayura client raises ExternalServiceError on failure."""
    client = SarvamMayuraClient(api_key="test-key", base_url="https://api.sarvam.ai")

    mock_resp = AsyncMock(spec=httpx.Response)
    mock_resp.status_code = 502
    mock_resp.text = "Bad Gateway"

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        with pytest.raises(ExternalServiceError) as exc_info:
            await client.translate_text(text="Test")

    assert "Sarvam Mayura" in str(exc_info.value)
