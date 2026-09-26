"""Abstract base interface for LLM providers."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LLMMessage(BaseModel):
    """Normalized chat message representation for LLM prompts."""

    role: str = Field(description="Role: system, user, or assistant")
    content: str = Field(description="Textual content of the message")


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM client integrations."""

    @abstractmethod
    async def generate_response(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.0,
        max_tokens: Optional[int] = 1024,
    ) -> str:
        """Generate a response completion for the specified conversation messages."""
        pass
