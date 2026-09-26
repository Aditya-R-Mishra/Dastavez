"""Thin integration client for Sarvam Saaras Speech-to-Text (STT) API."""

from typing import Any, Dict, Optional
import httpx

from app.core.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger

logger = get_logger(__name__)


class SarvamSaarasClient:
    """Client for Sarvam Saaras v3 speech transcription API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key or settings.SARVAM_API_KEY
        self.base_url = (base_url or settings.SARVAM_BASE_URL).rstrip("/")
        self.model_name = model_name or settings.STT_MODEL_NAME
        self.timeout = timeout

    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        content_type: str = "audio/wav",
        language_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Transcribe short conversational audio clips into text and detect language."""
        endpoint = f"{self.base_url}/speech-to-text"
        headers = {
            "api-subscription-key": self.api_key,
        }
        data: Dict[str, Any] = {
            "model": self.model_name,
        }
        if language_code:
            data["language_code"] = language_code

        files = {
            "file": (filename, audio_bytes, content_type)
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, headers=headers, data=data, files=files)
                if response.status_code != 200:
                    logger.error(
                        "Sarvam Saaras STT failed with status %d: %s",
                        response.status_code,
                        response.text,
                    )
                    raise ExternalServiceError(
                        service_name="Sarvam Saaras STT",
                        reason=f"Status {response.status_code}: {response.text}",
                    )

                data = response.json()
                transcript = data.get("transcript", "")
                language = data.get("language_code", "hi-IN")
                return {
                    "transcript": transcript,
                    "detected_language": language,
                }

        except httpx.RequestError as exc:
            logger.error("HTTP network failure connecting to Sarvam Saaras: %s", str(exc))
            raise ExternalServiceError("Sarvam Saaras STT", str(exc)) from exc
