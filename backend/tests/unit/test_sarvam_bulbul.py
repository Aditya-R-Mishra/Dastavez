"""Unit tests for Sarvam Bulbul Text-to-Speech (TTS) client."""

import base64
from unittest.mock import AsyncMock, patch
import httpx
import pytest

from app.core.exceptions import ExternalServiceError
from app.integrations.sarvam.bulbul_client import SarvamBulbulClient


@pytest.mark.asyncio
async def test_bulbul_speech_generation_success() -> None:
    """Verify Bulbul TTS decodes base64 audio response correctly."""
    client = SarvamBulbulClient(api_key="test-key", base_url="https://api.sarvam.ai")

    fake_audio_bytes = b"RIFFfakeaudio"
    b64_audio = base64.b64encode(fake_audio_bytes).decode("utf-8")

    mock_resp = AsyncMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"audios": [b64_audio]}

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        result_bytes = await client.generate_speech(text="नमस्ते, आपकी पालिसी सक्रिय है।", target_language_code="hi-IN")

    assert result_bytes == fake_audio_bytes


@pytest.mark.asyncio
async def test_bulbul_speech_generation_error() -> None:
    """Verify Bulbul client raises ExternalServiceError on failure."""
    client = SarvamBulbulClient(api_key="test-key", base_url="https://api.sarvam.ai")

    mock_resp = AsyncMock(spec=httpx.Response)
    mock_resp.status_code = 500
    mock_resp.text = "Internal Server Error"

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        with pytest.raises(ExternalServiceError) as exc_info:
            await client.generate_speech(text="Hello")

    assert "Sarvam Bulbul TTS" in str(exc_info.value)
