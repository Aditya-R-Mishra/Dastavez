"""Thin integration client for Sarvam Vision Document AI (Digitise) API."""

from typing import Any, Dict, Optional
import httpx

from app.core.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger

logger = get_logger(__name__)


class SarvamVisionClient:
    """Client for Sarvam Vision Document AI OCR and Layout extraction."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key or settings.SARVAM_API_KEY
        self.base_url = (base_url or settings.SARVAM_BASE_URL).rstrip("/")
        self.timeout = timeout

    async def digitize_document(
        self,
        file_bytes: bytes,
        filename: str = "document.pdf",
        language_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a document or batch (<=10 pages) to Sarvam Vision for OCR extraction."""
        endpoint = f"{self.base_url}/document/digitise"
        headers = {
            "api-subscription-key": self.api_key,
        }
        data: Dict[str, Any] = {}
        if language_code:
            data["language_code"] = language_code

        files = {
            "file": (filename, file_bytes, "application/pdf" if filename.endswith(".pdf") else "image/png")
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, headers=headers, data=data, files=files)
                if response.status_code != 200:
                    logger.error(
                        "Sarvam Vision failed with status %d: %s",
                        response.status_code,
                        response.text,
                    )
                    raise ExternalServiceError(
                        service_name="Sarvam Vision",
                        reason=f"Status {response.status_code}: {response.text}",
                    )

                return response.json()

        except httpx.RequestError as exc:
            logger.error("HTTP network failure connecting to Sarvam Vision: %s", str(exc))
            raise ExternalServiceError("Sarvam Vision", str(exc)) from exc
