"""Unit tests for VoiceService orchestration."""

from unittest.mock import AsyncMock
import pytest

from app.core.exceptions import AppException
from app.services.voice_service import VoiceService


@pytest.mark.asyncio
async def test_voice_service_process_query_success() -> None:
    """Verify VoiceService transcribes audio, routes to ChatService, and returns answer."""
    mock_stt = AsyncMock()
    mock_stt.transcribe_audio.return_value = {
        "transcript": "What is the policy deductible?",
        "detected_language": "en-IN",
    }

    mock_chat = AsyncMock()
    mock_chat.send_message.return_value = {
        "answer": "The deductible is $500.",
        "conversation_id": "conv-123",
        "sources": [{"document": "policy.pdf", "page": 1}],
    }

    mock_storage = AsyncMock()
    mock_storage.upload_file.return_value = "https://storage.example.com/audio.wav"

    service = VoiceService(
        stt_client=mock_stt,
        chat_service=mock_chat,
        storage_client=mock_storage,
    )

    result = await service.process_voice_query(
        user_id="user-456",
        audio_bytes=b"dummy-audio-bytes",
        filename="query.wav",
    )

    assert result["transcript"] == "What is the policy deductible?"
    assert result["detected_language"] == "en-IN"
    assert result["answer"] == "The deductible is $500."
    assert result["conversation_id"] == "conv-123"
    assert len(result["sources"]) == 1
    mock_stt.transcribe_audio.assert_called_once()
    mock_chat.send_message.assert_called_once_with(
        user_id="user-456",
        message="What is the policy deductible?",
        conversation_id=None,
        language="en-IN",
    )


@pytest.mark.asyncio
async def test_voice_service_empty_transcript_raises_app_exception() -> None:
    """Verify empty transcription raises 422 AppException."""
    mock_stt = AsyncMock()
    mock_stt.transcribe_audio.return_value = {"transcript": "", "detected_language": "en-IN"}

    service = VoiceService(stt_client=mock_stt)

    with pytest.raises(AppException) as exc_info:
        await service.process_voice_query(user_id="user-1", audio_bytes=b"silence")

    assert exc_info.value.status_code == 422
    assert exc_info.value.error_code == "STT_TRANSCRIPTION_FAILED"
