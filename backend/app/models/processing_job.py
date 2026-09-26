"""SQLAlchemy model for document processing jobs."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.constants import DocumentStatus, ProcessingStage
from app.models.document import Base


class ProcessingJob(Base):
    """Database model representing an asynchronous document processing job."""

    __tablename__ = "processing_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default=DocumentStatus.UPLOADED.value)
    progress = Column(Integer, nullable=False, default=0)
    current_stage = Column(String(100), nullable=False, default=ProcessingStage.UPLOADED.value)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    document = relationship("Document", back_populates="jobs")
