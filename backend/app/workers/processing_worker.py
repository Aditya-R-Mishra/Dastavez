"""Background processing pipeline worker executing document ingestion end-to-end."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from qdrant_client.models import PointStruct

from app.core.constants import DocumentStatus, PageStatus, ProcessingStage
from app.core.logging import get_logger
from app.integrations.qdrant_client import QdrantVectorClient
from app.integrations.supabase_client import SupabaseStorageClient
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.job_repository import JobRepository
from app.services.embedding_service import EmbeddingService
from app.services.pipeline.chunking import DocumentChunker
from app.services.pipeline.cleaning import TextCleaner
from app.services.pipeline.docx_txt_csv import DirectFormatParser
from app.services.pipeline.ocr_latin import LatinOCRPipeline
from app.services.pipeline.router import PipelineRouter
from app.services.pipeline.text_extraction import ExtractedPage, PDFTextExtractor

logger = get_logger(__name__)


class DocumentProcessingWorker:
    """Orchestrates end-to-end extraction, OCR, cleaning, chunking, and vector indexing."""

    def __init__(
        self,
        doc_repo: Optional[DocumentRepository] = None,
        job_repo: Optional[JobRepository] = None,
        chunk_repo: Optional[ChunkRepository] = None,
        storage_client: Optional[SupabaseStorageClient] = None,
        vector_client: Optional[QdrantVectorClient] = None,
        embedding_service: Optional[EmbeddingService] = None,
    ) -> None:
        self.doc_repo = doc_repo or DocumentRepository()
        self.job_repo = job_repo or JobRepository()
        self.chunk_repo = chunk_repo or ChunkRepository()
        self.storage_client = storage_client or SupabaseStorageClient()
        self.vector_client = vector_client or QdrantVectorClient()
        self.embedding_service = embedding_service or EmbeddingService()

        # Pipeline stages
        self.pdf_extractor = PDFTextExtractor()
        self.direct_parser = DirectFormatParser()
        self.ocr_pipeline = LatinOCRPipeline()
        self.cleaner = TextCleaner()
        self.chunker = DocumentChunker()

    async def _update_progress(
        self,
        job_id: str,
        stage: ProcessingStage,
        progress: int,
        status: DocumentStatus = DocumentStatus.PROCESSING,
        error_message: Optional[str] = None,
    ) -> None:
        """Helper to update real-time progress and logging."""
        await self.job_repo.update_job_progress(
            job_id=job_id,
            status=status.value,
            progress=progress,
            current_stage=stage.value,
            error_message=error_message,
        )

    async def process_document(
        self,
        document_id: str,
        job_id: str,
        user_id: str,
    ) -> None:
        """Execute the full ingestion pipeline asynchronously and idempotently."""
        logger.info(
            "Worker started pipeline for document %s (job: %s)",
            document_id,
            job_id,
            extra={"document_id": document_id, "job_id": job_id, "user_id": user_id},
        )

        try:
            # 1. Fetch document metadata and download file bytes
            await self._update_progress(job_id, ProcessingStage.UPLOADED, 5)
            doc = await self.doc_repo.get_document_by_id(document_id)
            if not doc:
                raise ValueError(f"Document {document_id} not found in database")

            storage_path = doc.get("storage_path")
            filename = doc.get("filename", "")
            file_type = doc.get("file_type", "pdf")

            file_bytes = await self.storage_client.download_file(storage_path)

            # 2. Routing and text extraction
            await self._update_progress(job_id, ProcessingStage.DETECTING_TYPE, 15)
            category = PipelineRouter.get_file_category(file_type)

            raw_pages: List[ExtractedPage] = []
            if category == "pdf":
                await self._update_progress(job_id, ProcessingStage.EXTRACTING_TEXT, 25)
                raw_pages = await self.pdf_extractor.extract_pages(file_bytes)
            elif category == "direct":
                await self._update_progress(job_id, ProcessingStage.EXTRACTING_TEXT, 25)
                raw_pages = await self.direct_parser.parse(file_bytes, file_type)
            elif category == "image":
                raw_pages = [ExtractedPage(page_number=1, raw_text="", is_scanned=True, image_bytes=file_bytes)]

            # Check existing pages for idempotency
            existing_pages = await self.doc_repo.get_pages_by_document(document_id)
            completed_page_nums = {
                p["page_number"]
                for p in existing_pages
                if p.get("page_status") == PageStatus.COMPLETED.value
            }

            # 3. Process each page (OCR + Cleaning)
            await self._update_progress(job_id, ProcessingStage.OCR_PROCESSING, 40)
            cleaned_pages_for_chunking = []

            for p in raw_pages:
                # Idempotency: skip page if already marked COMPLETED
                if p.page_number in completed_page_nums:
                    logger.info(
                        "Skipping already-completed page %d for document %s",
                        p.page_number,
                        document_id,
                    )
                    existing_p = next(
                        ep for ep in existing_pages if ep["page_number"] == p.page_number
                    )
                    cleaned_pages_for_chunking.append((
                        existing_p["id"],
                        existing_p["page_number"],
                        existing_p["raw_text"],
                    ))
                    continue

                page_text = p.raw_text
                ocr_used = False
                ocr_engine = "none"

                if p.is_scanned and p.image_bytes:
                    ocr_res = await self.ocr_pipeline.process_image(p.image_bytes)
                    page_text = ocr_res.text
                    ocr_used = True
                    ocr_engine = ocr_res.engine_name

                # Clean extracted text
                cleaned_text = self.cleaner.clean(page_text)

                # Persist page record with COMPLETED status
                page_rec = await self.doc_repo.create_or_update_page(
                    document_id=document_id,
                    page_number=p.page_number,
                    raw_text=cleaned_text,
                    ocr_used=ocr_used,
                    ocr_engine=ocr_engine,
                    language="en",
                    page_status=PageStatus.COMPLETED.value,
                )

                cleaned_pages_for_chunking.append((
                    page_rec.get("id", str(p.page_number)),
                    p.page_number,
                    cleaned_text,
                ))

            # 4. Chunking
            await self._update_progress(job_id, ProcessingStage.CHUNKING, 65)
            all_chunks: List[Dict[str, Any]] = []
            chunk_idx = 0

            for page_id, page_num, text in cleaned_pages_for_chunking:
                chunks = self.chunker.chunk_page(
                    document_id=document_id,
                    page_id=page_id,
                    page_number=page_num,
                    text=text,
                    start_chunk_index=chunk_idx,
                    filename=filename,
                )
                all_chunks.extend(chunks)
                chunk_idx += len(chunks)

            # Persist chunks in database
            if all_chunks:
                await self.chunk_repo.create_chunks(all_chunks)

            # 5. Embeddings and Vector Indexing
            await self._update_progress(job_id, ProcessingStage.GENERATING_EMBEDDINGS, 80)
            if all_chunks:
                chunk_texts = [c["content"] for c in all_chunks]
                embeddings = await self.embedding_service.generate_embeddings(chunk_texts)

                await self._update_progress(job_id, ProcessingStage.INDEXING, 90)
                await self.vector_client.ensure_collection_exists()

                points = []
                for chunk, vector in zip(all_chunks, embeddings):
                    points.append(
                        PointStruct(
                            id=chunk["chunk_id"],
                            vector=vector,
                            payload=chunk["metadata"],
                        )
                    )

                await self.vector_client.upsert_chunks(points)

            # 6. Mark Document and Job as COMPLETED
            now_iso = datetime.now(timezone.utc).isoformat()
            await self.doc_repo.update_document_status(
                document_id=document_id,
                status=DocumentStatus.COMPLETED.value,
                total_pages=len(raw_pages),
                processed_at=now_iso,
            )

            await self._update_progress(
                job_id=job_id,
                stage=ProcessingStage.COMPLETED,
                progress=100,
                status=DocumentStatus.COMPLETED,
            )

            logger.info(
                "Pipeline completed successfully for document %s (total pages: %d, chunks: %d)",
                document_id,
                len(raw_pages),
                len(all_chunks),
                extra={"document_id": document_id, "job_id": job_id},
            )

        except Exception as exc:
            logger.exception(
                "Document processing failed for document %s: %s",
                document_id,
                str(exc),
                extra={"document_id": document_id, "job_id": job_id},
            )
            await self.doc_repo.update_document_status(
                document_id=document_id,
                status=DocumentStatus.FAILED.value,
            )
            await self._update_progress(
                job_id=job_id,
                stage=ProcessingStage.FAILED,
                progress=0,
                status=DocumentStatus.FAILED,
                error_message=str(exc),
            )
            raise


async def run_document_pipeline_task(
    document_id: str,
    job_id: str,
    user_id: str,
) -> None:
    """Entry point for background task execution."""
    worker = DocumentProcessingWorker()
    await worker.process_document(document_id, job_id, user_id)
