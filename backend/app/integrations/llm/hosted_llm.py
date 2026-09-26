"""Hosted LLM provider implementation supporting OpenAI-compatible APIs (OpenAI, Gemini, Groq)."""

from typing import List, Optional
import httpx

from app.core.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger
from app.integrations.llm.base import BaseLLMProvider, LLMMessage

logger = get_logger(__name__)


class HostedLLMProvider(BaseLLMProvider):
    """Client for OpenAI-compatible chat completion APIs."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key or settings.LLM_API_KEY
        self.base_url = (base_url or settings.LLM_BASE_URL).rstrip("/")
        self.model_name = model_name or settings.LLM_MODEL_NAME
        self.timeout = timeout

    async def generate_response(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.0,
        max_tokens: Optional[int] = 1024,
    ) -> str:
        """Call the OpenAI-compatible chat completions API."""
        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "model": self.model_name,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, json=payload, headers=headers)
                if response.status_code != 200:
                    logger.error(
                        "LLM API returned error status %d: %s",
                        response.status_code,
                        response.text,
                    )
                    raise ExternalServiceError(
                        service_name="Hosted LLM",
                        reason=f"Status {response.status_code}: {response.text}",
                    )

                data = response.json()
                choices = data.get("choices", [])
                if not choices:
                    raise ExternalServiceError("Hosted LLM", "No choices returned in API response")

                return choices[0]["message"]["content"]

        except httpx.RequestError as exc:
            logger.error("HTTP network failure connecting to LLM provider: %s", str(exc))
            raise ExternalServiceError("Hosted LLM", str(exc)) from exc
