"""Voice query transcription, storage, and retrieval orchestration."""

import uuid
from typing import Any, Dict, Optional

from app.core.exceptions import AppException
from app.core.logging import get_logger
from app.integrations.sarvam.bulbul_client import SarvamBulbulClient
from app.integrations.sarvam.saaras_client import SarvamSaarasClient
from app.integrations.supabase_client import SupabaseStorageClient
from app.services.chat_service import ChatService

logger = get_logger(__name__)


class VoiceService:
    """Service orchestrating spoken question transcription, audio archiving, and RAG chat."""

    def __init__(
        self,
        stt_client: Optional[SarvamSaarasClient] = None,
        chat_service: Optional[ChatService] = None,
        storage_client: Optional[SupabaseStorageClient] = None,
        tts_client: Optional[SarvamBulbulClient] = None,
    ) -> None:
        self.stt_client = stt_client or SarvamSaarasClient()
        self.chat_service = chat_service or ChatService()
        self.storage_client = storage_client or SupabaseStorageClient()
        self.tts_client = tts_client or SarvamBulbulClient()

    async def process_voice_query(
        self,
        user_id: str,
        audio_bytes: bytes,
        filename: str = "voice_query.wav",
        content_type: str = "audio/wav",
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Transcribe spoken question audio with Sarvam Saaras and execute RAG retrieval."""
        logger.info(
            "Processing voice query audio clip (%d bytes, user: %s)",
            len(audio_bytes),
            user_id,
        )

        # 1. Transcribe audio using Sarvam Saaras v3 STT
        stt_result = await self.stt_client.transcribe_audio(
            audio_bytes=audio_bytes,
            filename=filename,
            content_type=content_type,
        )

        transcript = stt_result.get("transcript", "").strip()
        detected_language = stt_result.get("detected_language", "en-IN")

        if not transcript:
            raise AppException(
                message="Could not transcribe audio clip clearly. Please confirm or re-record.",
                status_code=422,
                error_code="STT_TRANSCRIPTION_FAILED",
            )

        logger.info(
            "Voice query transcribed: '%s' (detected language: %s)",
            transcript,
            detected_language,
        )

        # 2. Archive spoken audio clip to Supabase Storage
        audio_url = None
        try:
            audio_storage_path = f"{user_id}/voice/{uuid.uuid4()}_{filename}"
            audio_url = await self.storage_client.upload_file(
                file_path=audio_storage_path,
                file_bytes=audio_bytes,
                content_type=content_type,
            )
        except Exception as exc:
            logger.warning("Audio archiving failed (proceeding with text chat): %s", str(exc))

        # 3. Route transcribed query to standard ChatService
        chat_response = await self.chat_service.send_message(
            user_id=user_id,
            message=transcript,
            conversation_id=conversation_id,
            language=detected_language,
        )

        answer_text = chat_response["answer"]

        # 4. Synthesize spoken response audio via Sarvam Bulbul TTS
        audio_reply_url = None
        try:
            tts_audio_bytes = await self.tts_client.generate_speech(
                text=answer_text,
                target_language_code=detected_language if "-" in detected_language else "hi-IN",
            )
            reply_path = f"{user_id}/voice/reply_{uuid.uuid4()}.wav"
            audio_reply_url = await self.storage_client.upload_file(
                file_path=reply_path,
                file_bytes=tts_audio_bytes,
                content_type="audio/wav",
            )
        except Exception as exc:
            logger.warning("Spoken response synthesis failed (proceeding with text): %s", str(exc))

        return {
            "transcript": transcript,
            "detected_language": detected_language,
            "answer": answer_text,
            "conversation_id": chat_response["conversation_id"],
            "sources": chat_response["sources"],
            "audio_reply_url": audio_reply_url,
        }
