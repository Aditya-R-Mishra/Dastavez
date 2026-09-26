"""Unit tests for configuration loading and validation."""

import pytest
from app.core.config import Settings


def test_default_settings() -> None:
    """Verify default settings configuration."""
    test_settings = Settings()
    assert test_settings.APP_NAME == "Dastavez Document Intelligence API"
    assert test_settings.API_V1_STR == "/api/v1"
    assert test_settings.EMBEDDING_DIMENSION == 1024
    assert test_settings.CHUNK_SIZE_TOKENS == 500


def test_cors_origins_parsing() -> None:
    """Verify comma-separated string parsing for CORS origins."""
    test_settings = Settings(CORS_ORIGINS="http://localhost:3000,http://app.dastavez.ai")
    assert "http://localhost:3000" in test_settings.CORS_ORIGINS
    assert "http://app.dastavez.ai" in test_settings.CORS_ORIGINS
