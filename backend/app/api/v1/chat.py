"""Conversational RAG, multi-turn chat, and voice query API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile

from app.core.security import AuthenticatedUser, get_current_user
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationDetailResponse,
    ConversationListResponse,
    ConversationResponse,
    MessageResponse,
    SourceReference,
    VoiceChatResponse,
)
from app.schemas.common import StandardResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])


def get_chat_service() -> ChatService:
    """Dependency provider for ChatService."""
    return ChatService()


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """Send a conversational query and receive an evidence-grounded answer with citations."""
    result = await chat_service.send_message(
        user_id=current_user.id,
        message=request.message,
        conversation_id=request.conversation_id,
        document_ids=request.document_ids,
        language=request.language,
    )
    sources = [
        SourceReference(
            document=s.get("document", "unknown"),
            page=s.get("page", 1),
            section=s.get("section"),
            chunk_id=s.get("chunk_id"),
        )
        for s in result.get("sources", [])
    ]
    return ChatResponse(
        answer=result["answer"],
        conversation_id=result["conversation_id"],
        sources=sources,
        detected_language=result.get("detected_language"),
    )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: AuthenticatedUser = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> ConversationListResponse:
    """List conversation threads for the authenticated user."""
    convs, total = await chat_service.list_conversations(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )
    items = [ConversationResponse(**c) for c in convs]
    return ConversationListResponse(conversations=items, total=total)


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> ConversationDetailResponse:
    """Retrieve full message history for a specific conversation thread."""
    data = await chat_service.get_conversation(conversation_id, current_user.id)
    conv_data = data["conversation"]
    messages_data = data["messages"]
    return ConversationDetailResponse(
        conversation=ConversationResponse(**conv_data),
        messages=[MessageResponse(**m) for m in messages_data],
    )


@router.delete("/{conversation_id}", response_model=StandardResponse[None])
async def delete_conversation(
    conversation_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
) -> StandardResponse[None]:
    """Delete a conversation thread and all its messages."""
    await chat_service.delete_conversation(conversation_id, current_user.id)
    return StandardResponse(
        success=True,
        message=f"Conversation '{conversation_id}' deleted successfully",
        data=None,
    )


def get_voice_service() -> "VoiceService":
    """Dependency provider for VoiceService."""
    from app.services.voice_service import VoiceService
    return VoiceService()


@router.post("/voice", response_model=VoiceChatResponse)
async def voice_chat(
    file: UploadFile = File(..., description="Spoken question audio clip"),
    conversation_id: Optional[str] = Form(default=None),
    current_user: AuthenticatedUser = Depends(get_current_user),
    voice_service: "VoiceService" = Depends(get_voice_service),
) -> VoiceChatResponse:
    """Submit a spoken voice question to be transcribed via Sarvam Saaras and answered."""
    audio_bytes = await file.read()
    filename = file.filename or "voice_query.wav"
    content_type = file.content_type or "audio/wav"

    result = await voice_service.process_voice_query(
        user_id=current_user.id,
        audio_bytes=audio_bytes,
        filename=filename,
        content_type=content_type,
        conversation_id=conversation_id,
    )

    sources = [
        SourceReference(
            document=s.get("document", "unknown"),
            page=s.get("page", 1),
            section=s.get("section"),
            chunk_id=s.get("chunk_id"),
        )
        for s in result.get("sources", [])
    ]

    return VoiceChatResponse(
        transcript=result["transcript"],
        detected_language=result["detected_language"],
        answer=result["answer"],
        sources=sources,
        audio_reply_url=result.get("audio_reply_url"),
    )
