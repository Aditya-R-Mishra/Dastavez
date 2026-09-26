"""Unit tests for Sarvam Saaras Speech-to-Text (STT) client."""

from unittest.mock import AsyncMock, patch
import httpx
import pytest

from app.core.exceptions import ExternalServiceError
from app.integrations.sarvam.saaras_client import SarvamSaarasClient


@pytest.mark.asyncio
async def test_sarvam_saaras_transcribe_success() -> None:
    """Verify Saaras client properly parses successful transcription response."""
    client = SarvamSaarasClient(api_key="test-key", base_url="https://api.sarvam.ai")

    mock_resp = AsyncMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "transcript": "यह एक परीक्षण ऑडियो है।",
        "language_code": "hi-IN",
    }

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        res = await client.transcribe_audio(
            audio_bytes=b"fake-wav-bytes",
            filename="test.wav",
            content_type="audio/wav",
        )

    assert res["transcript"] == "यह एक परीक्षण ऑडियो है।"
    assert res["detected_language"] == "hi-IN"


@pytest.mark.asyncio
async def test_sarvam_saaras_transcribe_failure_raises_external_service_error() -> None:
    """Verify Saaras client raises ExternalServiceError when API returns non-200."""
    client = SarvamSaarasClient(api_key="test-key", base_url="https://api.sarvam.ai")

    mock_resp = AsyncMock(spec=httpx.Response)
    mock_resp.status_code = 400
    mock_resp.text = "Bad Request"

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        with pytest.raises(ExternalServiceError) as exc_info:
            await client.transcribe_audio(audio_bytes=b"fake-wav-bytes")

    assert "Sarvam Saaras STT" in str(exc_info.value)
