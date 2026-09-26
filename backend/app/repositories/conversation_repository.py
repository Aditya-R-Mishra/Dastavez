"""Pure database access repository for conversations and messages."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from starlette.concurrency import run_in_threadpool

from app.core.constants import InputMode, MessageRole
from app.integrations.supabase_client import get_supabase_client


class ConversationRepository:
    """Repository handling CRUD operations for conversations and messages."""

    def __init__(self, supabase=None) -> None:
        self.supabase = supabase or get_supabase_client()

    def _sync_create_conversation(self, user_id: str, title: str) -> Dict[str, Any]:
        data = {
            "user_id": user_id,
            "title": title,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        res = self.supabase.table("conversations").insert(data).execute()
        return res.data[0] if res.data else {}

    async def create_conversation(self, user_id: str, title: str = "New Conversation") -> Dict[str, Any]:
        """Create a new conversation thread for a user."""
        return await run_in_threadpool(self._sync_create_conversation, user_id, title)

    def _sync_get_conversation(self, conversation_id: str, user_id: Optional[str]) -> Optional[Dict[str, Any]]:
        query = self.supabase.table("conversations").select("*").eq("id", conversation_id)
        if user_id:
            query = query.eq("user_id", user_id)
        res = query.execute()
        return res.data[0] if res.data else None

    async def get_conversation(
        self,
        conversation_id: str,
        user_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve conversation thread metadata."""
        return await run_in_threadpool(self._sync_get_conversation, conversation_id, user_id)

    def _sync_list_conversations(self, user_id: str, limit: int, offset: int) -> Tuple[List[Dict[str, Any]], int]:
        res = (
            self.supabase.table("conversations")
            .select("*", count="exact")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        total = res.count if res.count is not None else len(res.data)
        return res.data or [], total

    async def list_conversations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """List conversations belonging to a user with pagination."""
        return await run_in_threadpool(self._sync_list_conversations, user_id, limit, offset)

    def _sync_delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        res = (
            self.supabase.table("conversations")
            .delete()
            .eq("id", conversation_id)
            .eq("user_id", user_id)
            .execute()
        )
        return bool(res.data)

    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Delete a conversation thread and its messages."""
        return await run_in_threadpool(self._sync_delete_conversation, conversation_id, user_id)

    # Message methods
    def _sync_create_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        res = self.supabase.table("messages").insert(message_data).execute()
        return res.data[0] if res.data else {}

    async def create_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        input_mode: str = InputMode.TEXT.value,
        language: Optional[str] = None,
        audio_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Append a message turn to a conversation thread."""
        message_data = {
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "input_mode": input_mode,
            "language": language,
            "audio_url": audio_url,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return await run_in_threadpool(self._sync_create_message, message_data)

    def _sync_get_messages(self, conversation_id: str, limit: int) -> List[Dict[str, Any]]:
        res = (
            self.supabase.table("messages")
            .select("*")
            .eq("conversation_id", conversation_id)
            .order("created_at", desc=False)
            .limit(limit)
            .execute()
        )
        return res.data or []

    async def get_messages(self, conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch chronological messages for a conversation thread."""
        return await run_in_threadpool(self._sync_get_messages, conversation_id, limit)
