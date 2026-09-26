"""Business logic service managing multi-turn conversations, query rewriting, and RAG chat."""

import uuid
from typing import Any, Dict, List, Optional, Tuple

from app.core.constants import InputMode, MessageRole
from app.core.exceptions import AppException
from app.core.logging import get_logger
from app.repositories.conversation_repository import ConversationRepository
from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService

logger = get_logger(__name__)


class ChatService:
    """Service orchestrating conversation history, retrieval, and grounded AI responses."""

    def __init__(
        self,
        conv_repo: Optional[ConversationRepository] = None,
        retrieval_service: Optional[RetrievalService] = None,
        llm_service: Optional[LLMService] = None,
    ) -> None:
        self.conv_repo = conv_repo or ConversationRepository()
        self.retrieval_service = retrieval_service or RetrievalService()
        self.llm_service = llm_service or LLMService()

    async def _rewrite_query_if_needed(
        self,
        query: str,
        history: List[Dict[str, Any]],
    ) -> str:
        """Rewrite conversational follow-up questions into standalone search queries."""
        if not history or len(history) < 2:
            return query

        # For follow-ups, combine last question context if short query is detected
        last_turn = history[-1]
        if len(query.split()) < 5:
            return f"{last_turn.get('content', '')} {query}"
        return query

    async def send_message(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process a conversational user query through the multi-source RAG pipeline."""
        # 1. Resolve or initialize conversation thread
        if conversation_id:
            conv = await self.conv_repo.get_conversation(conversation_id, user_id)
            if not conv:
                conv = await self.conv_repo.create_conversation(
                    user_id=user_id,
                    title=message[:50],
                )
                conversation_id = conv.get("id")
        else:
            conv = await self.conv_repo.create_conversation(
                user_id=user_id,
                title=message[:50],
            )
            conversation_id = conv.get("id")

        # 2. Persist user question message
        await self.conv_repo.create_message(
            conversation_id=str(conversation_id),
            role=MessageRole.USER.value,
            content=message,
            input_mode=InputMode.TEXT.value,
            language=language,
        )

        # 3. Retrieve recent conversation context
        history = await self.conv_repo.get_messages(str(conversation_id), limit=6)
        formatted_history = [
            {"role": m["role"], "content": m["content"]}
            for m in history[:-1]  # Exclude current message
        ]

        # 4. Query rewriting and semantic retrieval
        search_query = await self._rewrite_query_if_needed(message, formatted_history)
        chunks = await self.retrieval_service.search(
            query=search_query,
            user_id=user_id,
            document_ids=document_ids,
            limit=5,
            language=language,
        )

        # 5. Generate evidence-grounded answer
        answer, sources = await self.llm_service.generate_grounded_answer(
            query=message,
            retrieved_chunks=chunks,
            conversation_history=formatted_history,
        )

        # 6. Persist assistant reply message
        await self.conv_repo.create_message(
            conversation_id=str(conversation_id),
            role=MessageRole.ASSISTANT.value,
            content=answer,
            input_mode=InputMode.TEXT.value,
            language=language,
        )

        return {
            "answer": answer,
            "conversation_id": str(conversation_id),
            "sources": sources,
            "detected_language": language or "en",
        }

    async def list_conversations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Fetch paginated conversation threads for a user."""
        return await self.conv_repo.list_conversations(user_id=user_id, limit=limit, offset=offset)

    async def get_conversation(
        self,
        conversation_id: str,
        user_id: str,
    ) -> Dict[str, Any]:
        """Retrieve conversation thread metadata with message history."""
        conv = await self.conv_repo.get_conversation(conversation_id, user_id)
        if not conv:
            raise AppException("Conversation not found", status_code=404, error_code="CONVERSATION_NOT_FOUND")

        messages = await self.conv_repo.get_messages(conversation_id)
        return {
            "conversation": conv,
            "messages": messages,
        }

    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Delete a conversation thread and all its messages."""
        return await self.conv_repo.delete_conversation(conversation_id, user_id)
