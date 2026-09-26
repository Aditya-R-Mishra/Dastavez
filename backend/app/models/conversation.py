"""SQLAlchemy models for conversations and messages."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.constants import InputMode, MessageRole
from app.models.document import Base


class Conversation(Base):
    """Database model representing a conversation thread."""

    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(255), nullable=False, default="New Conversation")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """Database model representing a message in a conversation thread."""

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False, default=MessageRole.USER.value)
    content = Column(Text, nullable=False)
    input_mode = Column(String(20), nullable=False, default=InputMode.TEXT.value)
    language = Column(String(20), nullable=True)
    audio_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    conversation = relationship("Conversation", back_populates="messages")
