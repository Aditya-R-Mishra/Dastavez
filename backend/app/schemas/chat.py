"""Pydantic schemas for chat conversations, messages, and voice queries."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.core.constants import InputMode, MessageRole


class SourceReference(BaseModel):
    """Grounded source citation item referencing specific document evidence."""

    document: str
    page: int
    section: Optional[str] = None
    chunk_id: Optional[str] = None


class ChatRequest(BaseModel):
    """User conversational query request."""

    message: str = Field(min_length=1, description="User question or follow-up")
    conversation_id: Optional[str] = Field(default=None, description="Active conversation thread ID")
    document_ids: Optional[List[str]] = Field(default=None, description="Optional document scope filter")
    language: Optional[str] = Field(default=None, description="Optional query language code")


class ChatResponse(BaseModel):
    """Grounded conversational response with citations."""

    answer: str
    conversation_id: str
    sources: List[SourceReference] = Field(default_factory=list)
    detected_language: Optional[str] = None


class VoiceChatResponse(BaseModel):
    """Response to a spoken audio query."""

    transcript: str
    detected_language: str
    answer: str
    sources: List[SourceReference] = Field(default_factory=list)
    audio_reply_url: Optional[str] = None


class MessageResponse(BaseModel):
    """Individual conversation message representation."""

    id: str
    conversation_id: str
    role: MessageRole
    content: str
    input_mode: InputMode = InputMode.TEXT
    language: Optional[str] = None
    audio_url: Optional[str] = None
    created_at: datetime


class ConversationResponse(BaseModel):
    """Conversation thread metadata representation."""

    id: str
    user_id: str
    title: str
    created_at: datetime


class ConversationListResponse(BaseModel):
    """List of user conversations."""

    conversations: List[ConversationResponse]
    total: int


class ConversationDetailResponse(BaseModel):
    """Conversation metadata together with chronological messages."""

    conversation: ConversationResponse
    messages: List[MessageResponse]
