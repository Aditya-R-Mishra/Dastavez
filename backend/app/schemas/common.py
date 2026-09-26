"""Common reusable Pydantic schemas."""

from datetime import datetime, timezone
from typing import Any, Dict, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class HealthResponse(BaseModel):
    """Health check endpoint response schema."""

    status: str = "healthy"
    version: str = "2.0.0"
    environment: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StandardResponse(BaseModel, Generic[DataT]):
    """Standard unified API response wrapper."""

    success: bool = True
    message: str = "Success"
    data: Optional[DataT] = None


class ErrorResponse(BaseModel):
    """Standardized error response schema."""

    success: bool = False
    error_code: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class PaginationParams(BaseModel):
    """Common pagination query parameters."""

    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
