"""Thin client for Sarvam Mayura Translation API."""

from typing import Any, Dict, Optional
import httpx

from app.core.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger

logger = get_logger(__name__)


class SarvamMayuraClient:
    """Client for Sarvam Mayura translation API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key or settings.SARVAM_API_KEY
        self.base_url = (base_url or settings.SARVAM_BASE_URL).rstrip("/")
        self.timeout = timeout

    async def translate_text(
        self,
        text: str,
        source_language_code: str = "en-IN",
        target_language_code: str = "hi-IN",
        mode: str = "formal",
    ) -> str:
        """Translate text between Indic and English languages using Sarvam Mayura."""
        endpoint = f"{self.base_url}/translate"
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "input": text,
            "source_language_code": source_language_code,
            "target_language_code": target_language_code,
            "mode": mode,
            "model": "mayura:v1",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, headers=headers, json=payload)
                if response.status_code != 200:
                    logger.error(
                        "Sarvam Mayura translation failed (%d): %s",
                        response.status_code,
                        response.text,
                    )
                    raise ExternalServiceError(
                        service_name="Sarvam Mayura",
                        reason=f"Status {response.status_code}: {response.text}",
                    )

                data = response.json()
                return data.get("translated_text", text)

        except httpx.RequestError as exc:
            logger.error("HTTP network failure connecting to Sarvam Mayura: %s", str(exc))
            raise ExternalServiceError("Sarvam Mayura", str(exc)) from exc
