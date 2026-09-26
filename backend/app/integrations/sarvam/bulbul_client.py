"""Thin client for Sarvam Bulbul Text-to-Speech (TTS) API."""

import base64
from typing import Any, Dict, Optional
import httpx

from app.core.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger

logger = get_logger(__name__)


class SarvamBulbulClient:
    """Client for Sarvam Bulbul text-to-speech synthesis API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key or settings.SARVAM_API_KEY
        self.base_url = (base_url or settings.SARVAM_BASE_URL).rstrip("/")
        self.model_name = model_name or settings.TTS_MODEL_NAME
        self.timeout = timeout

    async def generate_speech(
        self,
        text: str,
        target_language_code: str = "hi-IN",
        speaker: str = "meera",
        pitch: float = 0.0,
        pace: float = 1.0,
    ) -> bytes:
        """Synthesize text into spoken audio WAV/MP3 bytes."""
        endpoint = f"{self.base_url}/text-to-speech"
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "inputs": [text[:500]],  # Bulbul processes segments up to ~500 chars
            "target_language_code": target_language_code,
            "speaker": speaker,
            "pitch": pitch,
            "pace": pace,
            "model": self.model_name,
            "enable_preprocessing": True,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, headers=headers, json=payload)
                if response.status_code != 200:
                    logger.error(
                        "Sarvam Bulbul TTS failed with status %d: %s",
                        response.status_code,
                        response.text,
                    )
                    raise ExternalServiceError(
                        service_name="Sarvam Bulbul TTS",
                        reason=f"Status {response.status_code}: {response.text}",
                    )

                data = response.json()
                audios = data.get("audios", [])
                if not audios or not audios[0]:
                    raise ExternalServiceError("Sarvam Bulbul TTS", "Empty audio stream returned")

                return base64.b64decode(audios[0])

        except httpx.RequestError as exc:
            logger.error("HTTP network failure connecting to Sarvam Bulbul: %s", str(exc))
            raise ExternalServiceError("Sarvam Bulbul TTS", str(exc)) from exc
