"""Unit tests for ChatService multi-turn state and retrieval orchestration."""

from unittest.mock import AsyncMock
import pytest

from app.services.chat_service import ChatService


@pytest.mark.asyncio
async def test_chat_service_send_message() -> None:
    """Verify send_message initializes thread, retrieves evidence, and records assistant response."""
    mock_conv_repo = AsyncMock()
    mock_retrieval = AsyncMock()
    mock_llm = AsyncMock()

    mock_conv_repo.create_conversation.return_value = {"id": "conv-100", "title": "Test Chat"}
    mock_conv_repo.create_message.return_value = {"id": "msg-1"}
    mock_conv_repo.get_messages.return_value = [
        {"role": "user", "content": "What are eligibility criteria?"}
    ]

    mock_retrieval.search.return_value = [{
        "chunk_id": "c-1",
        "filename": "policy.pdf",
        "page": 1,
        "content": "Eligibility starts at 18.",
    }]

    mock_llm.generate_grounded_answer.return_value = (
        "Eligibility starts at 18.",
        [{"document": "policy.pdf", "page": 1, "chunk_id": "c-1"}],
    )

    service = ChatService(
        conv_repo=mock_conv_repo,
        retrieval_service=mock_retrieval,
        llm_service=mock_llm,
    )

    response = await service.send_message(
        user_id="user-1",
        message="What are eligibility criteria?",
    )

    assert response["conversation_id"] == "conv-100"
    assert response["answer"] == "Eligibility starts at 18."
    assert len(response["sources"]) == 1
    assert mock_conv_repo.create_message.call_count == 2  # 1 for user, 1 for assistant
    mock_retrieval.search.assert_called_once()
    mock_llm.generate_grounded_answer.assert_called_once()
