"""SQLAlchemy models for documents and document pages."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

from app.core.constants import DocumentStatus, PageStatus

Base = declarative_base()


class Document(Base):
    """Database model representing an uploaded document."""

    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)
    file_size = Column(Integer, nullable=False)
    storage_path = Column(String(500), nullable=True)
    status = Column(String(50), nullable=False, default=DocumentStatus.UPLOADED.value)
    total_pages = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
    jobs = relationship("ProcessingJob", back_populates="document", cascade="all, delete-orphan")


class DocumentPage(Base):
    """Database model representing a single page of an ingested document."""

    __tablename__ = "document_pages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    page_number = Column(Integer, nullable=False)
    raw_text = Column(Text, nullable=False, default="")
    ocr_used = Column(Boolean, default=False)
    ocr_engine = Column(String(50), nullable=False, default="none")
    language = Column(String(20), nullable=True)
    page_status = Column(String(50), nullable=False, default=PageStatus.PENDING.value)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    document = relationship("Document", back_populates="pages")
    chunks = relationship("Chunk", back_populates="page", cascade="all, delete-orphan")
