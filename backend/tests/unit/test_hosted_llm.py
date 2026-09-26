"""Unit tests for HostedLLMProvider client."""

from unittest.mock import AsyncMock, MagicMock, patch
import httpx
import pytest

from app.integrations.llm.base import LLMMessage
from app.integrations.llm.hosted_llm import HostedLLMProvider


@pytest.mark.asyncio
async def test_hosted_llm_generates_response() -> None:
    """Verify hosted LLM provider posts prompt and returns response text."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "This is the generated answer."}}]
    }

    provider = HostedLLMProvider(api_key="test-key", base_url="https://api.test.com/v1", model_name="test-model")

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        messages = [
            LLMMessage(role="system", content="System instruction"),
            LLMMessage(role="user", content="User question"),
        ]
        result = await provider.generate_response(messages)

    assert result == "This is the generated answer."
    mock_post.assert_called_once()
