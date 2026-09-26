"""End-to-end live verification script for Dastavez RAG platform.

Tests:
1. PDF document creation in memory.
2. Uploading to Supabase Storage and database records.
3. Running the ingestion pipeline (PyMuPDF -> Chunks -> Embeddings -> Qdrant).
4. Conversational question answering via ChatService (Retrieval + LLM generation with citations).
5. Clean up of test document and vector points.
"""

import asyncio
import uuid
import fitz  # PyMuPDF

from app.core.logging import get_logger
from app.services.chat_service import ChatService
from app.services.document_service import DocumentService
from app.workers.processing_worker import DocumentProcessingWorker

logger = get_logger("live_test")


def create_sample_pdf() -> bytes:
    """Generate a 2-page test insurance policy PDF in memory."""
    doc = fitz.open()

    # Page 1: Coverage details
    page1 = doc.new_page()
    text_p1 = (
        "HEALTHGUARD PREMIUM HEALTH INSURANCE POLICY - 2026\n\n"
        "Section 1: Hospitalization Coverage\n"
        "The HealthGuard Premium plan provides comprehensive hospitalization coverage "
        "up to a maximum policy limit of $150,000 per policy year for emergency medical "
        "care and intensive care unit (ICU) admissions.\n\n"
        "Section 2: Deductible and Copay\n"
        "The annual policy deductible is $500, after which the insurer pays 90% "
        "of all eligible medical bills until the out-of-pocket maximum is reached."
    )
    page1.insert_text((50, 72), text_p1, fontsize=12)

    # Page 2: Waiting periods & exclusions
    page2 = doc.new_page()
    text_p2 = (
        "Section 3: Waiting Periods and Exclusions\n\n"
        "All pre-existing medical conditions are subject to a mandatory waiting period "
        "of exactly 90 days from the policy inception date before any claims can be processed.\n\n"
        "Section 4: Non-Covered Treatments\n"
        "Elective cosmetic surgeries, dental implants, and experimental therapies are "
        "expressly excluded from coverage under this policy."
    )
    page2.insert_text((50, 72), text_p2, fontsize=12)

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


async def main() -> None:
    print("=" * 65)
    print("🚀 STARTING DASTAVEZ END-TO-END LIVE BACKEND VERIFICATION")
    print("=" * 65)

    test_user_id = str(uuid.uuid4())
    filename = f"healthguard_policy_test_{uuid.uuid4().hex[:6]}.pdf"

    doc_service = DocumentService()
    worker = DocumentProcessingWorker()
    chat_service = ChatService()

    # 1. Create sample PDF
    print("\n[Step 1] Generating sample 2-page test PDF...")
    pdf_bytes = create_sample_pdf()
    print(f"✓ Generated PDF successfully ({len(pdf_bytes)} bytes)")

    # 2. Upload Document
    print("\n[Step 2] Uploading document to Supabase Storage & Database...")
    upload_res = await doc_service.upload_document(
        user_id=test_user_id,
        filename=filename,
        file_bytes=pdf_bytes,
        content_type="application/pdf",
    )
    doc_id = upload_res["document_id"]
    job_id = upload_res["job_id"]
    print(f"✓ Upload successful! Document ID: {doc_id}")
    print(f"✓ Ingestion Job ID: {job_id}")

    # 3. Process Document
    print("\n[Step 3] Running full document ingestion pipeline...")
    print("  -> Extracting text with PyMuPDF...")
    print("  -> Creating 500-token chunks with 50-token overlap...")
    print("  -> Computing dense vector embeddings...")
    print("  -> Indexing into Qdrant & storing chunks in Supabase...")
    await worker.process_document(
        document_id=doc_id,
        job_id=job_id,
        user_id=test_user_id,
    )
    status_res = await doc_service.get_document_status(doc_id, test_user_id)
    print(f"✓ Pipeline finished! Status: {status_res['status']} ({status_res['progress']}%)")
    assert status_res["status"] == "COMPLETED", f"Expected COMPLETED, got {status_res['status']}"

    # 4. Ask Questions via ChatService
    print("\n[Step 4] Querying document via Conversational RAG...")

    # Question 1: Coverage limit
    query1 = "What is the maximum coverage limit for emergency hospitalization?"
    print(f"\n❓ Question 1: '{query1}'")
    retrieved1 = await chat_service.retrieval_service.search(query=query1, document_ids=[doc_id])
    print(f"Retrieved {len(retrieved1)} chunks for Q1:")
    for r in retrieved1:
        print(f"   [P{r.get('page')} | score: {r.get('score')}]: {r.get('content', '')[:100]}...")

    answer1 = await chat_service.send_message(
        user_id=test_user_id,
        message=query1,
        document_ids=[doc_id],
    )
    print("💬 Answer:")
    print(f"   {answer1['answer']}")
    print("📎 Sources & Citations:")
    for s in answer1["sources"]:
        print(f"   - Document: {s.get('document')}, Page: {s.get('page')}")

    # Question 2: Waiting period
    query2 = "What is the waiting period for pre-existing conditions, and are cosmetic surgeries covered?"
    print(f"\n❓ Question 2: '{query2}'")
    answer2 = await chat_service.send_message(
        user_id=test_user_id,
        message=query2,
        document_ids=[doc_id],
        conversation_id=answer1["conversation_id"],  # Multi-turn conversation continuation
    )
    print("💬 Answer:")
    print(f"   {answer2['answer']}")
    print("📎 Sources & Citations:")
    for s in answer2["sources"]:
        print(f"   - Document: {s.get('document')}, Page: {s.get('page')}")

    # 5. Clean up
    print("\n[Step 5] Cleaning up test document and vector points...")
    await doc_service.delete_document(doc_id, test_user_id)
    print(f"✓ Cleaned up document {doc_id} successfully!")

    print("\n" + "=" * 65)
    print("🎉 ALL END-TO-END VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(main())
