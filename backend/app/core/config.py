"""Application configuration management using pydantic-settings."""

from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application settings
    APP_NAME: str = "Dastavez Document Intelligence API"
    APP_ENV: str = "development"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: Union[List[str], str] = Field(
        default=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
    )

    # Supabase Configuration
    SUPABASE_URL: str = Field(default="http://localhost:54321")
    SUPABASE_KEY: str = Field(default="test-anon-key")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(default="test-service-role-key")
    SUPABASE_JWT_SECRET: str = Field(default="test-jwt-secret-key-at-least-32-chars-long")
    SUPABASE_STORAGE_BUCKET: str = "documents"

    # Qdrant Vector Search Configuration
    QDRANT_URL: str = Field(default="http://localhost:6333")
    QDRANT_API_KEY: str = Field(default="")
    QDRANT_COLLECTION_NAME: str = "dastavez_chunks"

    # Sarvam AI Configuration
    SARVAM_API_KEY: str = Field(default="")
    SARVAM_BASE_URL: str = "https://api.sarvam.ai"

    # LLM Configuration
    LLM_PROVIDER: str = "hosted"
    LLM_API_KEY: str = Field(default="")
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL_NAME: str = "gpt-4o-mini"
    SARVAM_LLM_MODEL: str = "sarvam-105b"

    # Embedding Configuration
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-m3"
    EMBEDDING_DIMENSION: int = 1024

    # Document Processing Parameters
    MAX_FILE_SIZE_BYTES: int = 50 * 1024 * 1024  # 50 MB
    CHUNK_SIZE_TOKENS: int = 500
    CHUNK_OVERLAP_TOKENS: int = 50

    # Voice / Audio Configuration
    STT_MODEL_NAME: str = "saaras:v3"
    TTS_MODEL_NAME: str = "bulbul:v1"

    # Background Tasks & Worker Queue
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_CELERY: bool = False

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Convert comma-separated origin string to a list if necessary."""
        if isinstance(v, str) and not v.startswith("["):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return v
        return []


settings = Settings()
