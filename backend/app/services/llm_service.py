"""Evidence-grounded response generation and citation attribution using LLM."""

import json
import re
from typing import Any, Dict, List, Optional, Tuple

from app.core.logging import get_logger
from app.integrations.llm.base import BaseLLMProvider, LLMMessage
from app.integrations.llm.hosted_llm import HostedLLMProvider

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are Dastavez, an expert document intelligence AI assistant.
Answer the user's question based STRICTLY and ONLY on the supplied document evidence excerpts below.

Rules you MUST ALWAYS follow:
1. Do NOT fabricate, assume, or extrapolate information not directly stated in the evidence.
2. If the provided evidence does NOT contain enough information to answer the question accurately, explicitly output: "I could not find sufficient information in the uploaded documents to answer this question."
3. If the evidence contains conflicting statements across sources or pages, clearly state the conflict and quote the differing sources.
4. Format your answer as valid JSON matching this schema:
{
  "answer": "Your comprehensive grounded answer text here.",
  "sources": [
    {
      "document": "Filename of source document",
      "page": 1,
      "section": "Section name or empty string",
      "chunk_id": "Exact chunk ID from excerpt"
    }
  ]
}
Do not enclose the JSON in backticks or markdown if possible; output only the JSON object.
"""


class LLMService:
    """Service handling prompt construction, grounded reasoning, and citation parsing."""

    def __init__(self, provider: Optional[BaseLLMProvider] = None) -> None:
        self.provider = provider or HostedLLMProvider()

    def _format_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Format retrieved chunks into numbered context blocks for the prompt."""
        if not chunks:
            return "No document evidence retrieved."

        blocks = []
        for i, c in enumerate(chunks, 1):
            doc = c.get("filename") or c.get("document_id") or "Unknown Document"
            page = c.get("page", 1)
            sec = c.get("section") or "General"
            cid = c.get("chunk_id", "")
            content = c.get("content", "").strip()
            blocks.append(
                f"[Evidence #{i} | Document: {doc} | Page: {page} | Section: {sec} | Chunk ID: {cid}]\n{content}"
            )
        return "\n\n".join(blocks)

    def _parse_llm_json(self, raw_text: str, default_chunks: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
        """Parse structured answer and sources from LLM output with robust fallback."""
        text = raw_text.strip()
        # Remove markdown code block fences if present
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\n?", "", text)
            text = re.sub(r"\n?```$", "", text).strip()

        try:
            data = json.loads(text)
            answer = data.get("answer", raw_text)
            sources = data.get("sources", [])
            return answer, sources
        except Exception:
            # Fallback when LLM returns plain text
            sources = []
            for c in default_chunks[:3]:
                sources.append({
                    "document": c.get("filename") or "document",
                    "page": c.get("page", 1),
                    "section": c.get("section"),
                    "chunk_id": c.get("chunk_id"),
                })
            return raw_text, sources

    async def generate_grounded_answer(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Generate evidence-grounded answer with source citations."""
        evidence_context = self._format_context(retrieved_chunks)

        messages: List[LLMMessage] = [
            LLMMessage(role="system", content=SYSTEM_PROMPT),
        ]

        # Append recent conversation history context if available
        if conversation_history:
            for turn in conversation_history[-4:]:
                messages.append(LLMMessage(role=turn["role"], content=turn["content"]))

        user_content = f"Retrieved Document Evidence:\n{evidence_context}\n\nUser Question:\n{query}"
        messages.append(LLMMessage(role="user", content=user_content))

        raw_response = await self.provider.generate_response(messages=messages, temperature=0.0)
        return self._parse_llm_json(raw_response, retrieved_chunks)
