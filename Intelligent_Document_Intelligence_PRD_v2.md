# Product Requirements Document (PRD)

# Intelligent Document Intelligence & Multi-Source Search

**Version:** 2.0
**Project Type:** Hackathon Web Application
**Target:** Third Year — Hackathon Problem Statement
**Changelog from v1.0:**
- Added Sarvam AI integration for Indic-language OCR, translation, and LLM reasoning (Section 10A, 20A)
- Added Voice Query System — users can speak questions instead of typing (Section 19A)
- Trimmed P0 scope to be realistically buildable in a hackathon timeframe
- Added page-level processing status to support partial-failure handling

---

## 1. Product Overview

The platform is an AI-powered document intelligence and multi-source search system.

Organizations often manage PDFs, scanned documents, reports, manuals, tables, and images — many in Indian regional languages. The system should allow users to upload these heterogeneous sources, automatically determine the appropriate processing pipeline, extract useful content and structure, index the content for semantic retrieval, and answer natural-language questions — typed **or spoken** — using relevant information from one or multiple documents.

Every generated answer should be grounded in retrieved evidence and provide document/page/section references wherever possible.

### Core pipeline

```text
Document Upload (file OR voice query)
      ↓
Document Type Detection
      ↓
Multi-Pipeline Processing (Text / OCR / Table / Indic-OCR)
      ↓
Cleaning + Structure Detection
      ↓
Chunking
      ↓
Embeddings
      ↓
Vector Index
      ↓
Semantic / Contextual Retrieval
      ↓
Multi-Source Context
      ↓
AI-Powered Response (text + optional spoken reply)
      ↓
Evidence + Source Attribution
```

---

# 2. Problem Statement

Build an intelligent platform that can ingest heterogeneous documents, process them through appropriate pipelines, and answer natural-language queries — typed or spoken, in English or Indian regional languages — by retrieving and combining relevant information from multiple sources.

---

# 3. Goals

The system must:

1.  Support PDFs.
2.  Support scanned documents.
3.  Support tables.
4.  Support image-based content.
5.  Route different document types through appropriate processing pipelines.
6.  Extract document structure, content, and metadata.
7.  Perform OCR on scanned and noisy documents, including Indian-script documents.
8.  Perform semantic and contextual retrieval.
9.  Retrieve information from multiple documents/sources.
10. Combine retrieved context before generating an answer.
11. Maintain conversational context for follow-up questions.
12. Provide source/page/section references.
13. Provide supporting evidence for generated answers.
14. Avoid fabricating information.
15. Clearly handle insufficient information.
16. Clearly handle conflicting information.
17. **Accept spoken questions via microphone and optionally reply with synthesized speech.**
18. **Support querying in Indian regional languages, independent of the language the source document is written in.**
19. Demonstrate the complete document intelligence pipeline in a working web application.

---

# 4. Non-Goals

The initial hackathon version does not need to:

-   Train a foundation LLM from scratch.
-   Build a proprietary OCR or ASR model from scratch.
-   Build a proprietary vector database.
-   Support every possible document format or all 22 Indian languages equally well (Sarvam's supported set is the practical ceiling).
-   Guarantee perfect OCR on extremely degraded documents.
-   Support real-time streaming voice conversation (turn-based voice query/response is sufficient).
-   Replace human review for legally or operationally critical decisions.

---

# 5. Target Users

### Primary User

An individual or organization user who needs to:

-   Upload documents (including regional-language scans).
-   Search across documents.
-   Ask questions in natural language — by typing or speaking.
-   Follow up with contextual questions.
-   Verify where an answer came from.

### Example User

A user uploads:

-   Insurance policy PDF (English)
-   Government guideline PDF (Hindi)
-   Company manual
-   Scanned circular in Marathi
-   Table-based report

The user **speaks** the question:

> "इन सभी दस्तावेज़ों में पात्रता की शर्तें क्या हैं?" (What are the eligibility requirements across all these documents?)

The platform transcribes the question, retrieves relevant information across all sources regardless of source language, and presents a consolidated answer with evidence — as text, and optionally as speech.

---

# 6. Functional Requirements

## FR-01: User Authentication

The system shall support user registration, login, logout/session management, authenticated document access, and user-specific document isolation.

**Technology:** Supabase Auth.

---

# 7. Document Upload

## FR-02: Upload Documents

Initial supported types: PDF, PNG/JPG/JPEG, DOCX, TXT, CSV.

### Upload requirements

The backend shall: receive the file, validate type and size, generate a unique document ID, store the file, create document metadata, start asynchronous processing, and return processing status.

### Example API

```http
POST /api/v1/documents/upload
```

```json
{
  "document_id": "uuid",
  "filename": "policy.pdf",
  "status": "PROCESSING"
}
```

---

# 8. Multi-Format Document Support

-   **Normal PDFs** — text extraction.
-   **Scanned PDFs** — render pages to images, run OCR.
-   **Image documents** — run OCR directly.
-   **Tables** — detect and extract while preserving row/column relationships.
-   **Indic-language documents (scanned or native)** — routed to Sarvam Vision (see Section 10A).
-   **DOCX documents** — parsed directly for text, headings, and tables (no OCR needed).
-   **TXT / CSV files** — read directly as structured/plain text; CSV rows treated as table-equivalent content.
-   **Mixed documents** — different pages/sections may use different processing methods.

---

# 9. Intelligent Document Processing

### Processing router

```text
Input
 ↓
File Detection
 ↓
Language / Script Detection
 ↓
Content Analysis
 ↓
Pipeline Router
 ├── Text Extraction (PyMuPDF)
 ├── OCR — Latin script (PaddleOCR)
 ├── OCR — Indic script (Sarvam Vision)
 ├── Table Extraction (Camelot, fallback to OCR text)
 ├── DOCX Parsing (python-docx)
 ├── TXT / CSV Direct Read
 └── Image Processing
```

### Required extracted metadata

At minimum: Document ID, Filename, File type, Page number, Extracted text, OCR usage, OCR engine used, Detected language, Processing status (per page), Creation timestamp, Processing timestamp.

Where available: Section, Heading, Table, Image, Bounding box, OCR confidence.

---

# 10. OCR & Noisy Document Handling

### OCR flow

```text
Scanned Page
 ↓
Language/Script Detection
 ↓
Image Preprocessing (deskew, denoise, binarize)
 ↓
OCR (PaddleOCR or Sarvam Vision, based on script)
 ↓
Detected Text
 ↓
Cleaning
 ↓
Page Storage
```

The system should retain whether OCR was used and which engine handled it.

```json
{
  "page_number": 5,
  "ocr_used": true,
  "ocr_engine": "sarvam_vision",
  "language": "hi-IN",
  "text": "..."
}
```

The OCR pipeline should attempt to handle low-quality scans, skewed pages, noisy backgrounds, and image-based PDFs.

## 10A. Indic-Language Document Processing (Sarvam AI)

**Rationale:** General-purpose OCR (Tesseract/PaddleOCR) is noticeably weaker on Indian scripts (Devanagari, Tamil, Telugu, Bengali, etc.), especially on noisy or low-quality scans. Sarvam Vision is purpose-built and benchmarked for this.

-   **Model:** Sarvam Vision (Document AI — Digitise endpoint), a 3B-parameter document-intelligence VLM.
-   **Coverage:** 23 languages (22 Indian + English), preserves layout, reading order, and converts tables to structured HTML/Markdown.
-   **Routing rule:** if script/language detection on a page identifies an Indian script (or the user explicitly tags the document as regional-language), route that page to Sarvam Vision instead of PaddleOCR.
-   **Known limitation:** 10 pages per job, 200 MB per file. The router must split larger documents into batches of ≤10 pages and re-stitch page numbers on the way back.
-   **Fallback:** if a Sarvam Vision job fails or times out, fall back to PaddleOCR and flag `ocr_confidence` as low so the UI can show a warning.

---

# 11. Table Processing

```text
Document
 ↓
Table Detection
 ↓
Table Extraction (Camelot, or Sarvam Vision table parsing for Indic tables)
 ↓
Structure Preservation
 ↓
Text Representation
 ↓
Chunking
 ↓
Embedding
```

Tables retain: Document ID, Page number, Table ID, Rows/columns, Extracted values.

---

# 12. Content Cleaning

Cleaning may include: removing repeated headers/footers, removing unnecessary whitespace, normalizing line breaks, preserving meaningful headings, preserving table relationships, removing extraction artifacts, maintaining page boundaries. The system must not remove information required to correctly answer user questions.

---

# 13. Chunking

Each chunk contains: `chunk_id, document_id, page_id, page_number, chunk_index, content, language, metadata`.

Recommended: semantic/section-aware chunking where possible, ~500–1000 tokens per chunk, small overlap between adjacent chunks. Chunking parameters remain configurable.

---

# 14. Embeddings

Each chunk shall be converted into an embedding vector.

**Model:** BGE-M3 (multilingual — chosen specifically because it embeds Indian-language and English text into the same vector space, enabling cross-lingual retrieval: a Hindi query can retrieve relevant English document chunks and vice versa).

```text
Chunk → Embedding Model (BGE-M3) → Vector → Qdrant
```

---

# 15. Vector Search

Qdrant is used for vector retrieval. Each vector retains payload metadata:

```json
{
  "chunk_id": "uuid",
  "document_id": "uuid",
  "page": 12,
  "filename": "policy.pdf",
  "section": "Eligibility",
  "language": "en"
}
```

The vector database shall support filtering by user/document where required.

---

# 16. Semantic & Contextual Retrieval

```text
User Query (text or transcribed voice)
 ↓
Query Processing / Translation (if needed)
 ↓
Dense Semantic Search (BGE-M3)
 ↓
Sparse/Keyword Search
 ↓
Result Fusion (RRF)
 ↓
Reranking (BGE Reranker)
 ↓
Top Relevant Context
```

---

# 17. Multi-Source Retrieval

The system retrieves information from multiple uploaded documents when the query requires it, regardless of each document's source language, and the answer must identify the relevant sources.

---

# 18. Conversational Context

The system maintains conversation history (`conversation_id, message_id, role, content, input_mode, language, timestamp`) so follow-up questions — typed or spoken — are understood in context of prior turns.

---

# 19. Query Rewriting

For follow-up questions, the backend converts conversational queries into standalone retrieval queries using recent conversation history before running retrieval.

## 19A. Voice Query System (New)

**Goal:** Let the user ask questions by speaking instead of typing, and optionally hear the answer spoken back.

### Voice input flow

```text
Microphone Capture (frontend)
 ↓
Audio Upload (webm/wav, short clip)
 ↓
Speech-to-Text — Sarvam Saaras/Saarika
 ↓
Language Detection + Transcript
 ↓
(Optional) Translate transcript to a pivot language for retrieval
 ↓
Query Rewriting (using chat history)
 ↓
Standard Retrieval Pipeline (Section 16)
```

### Voice output flow (optional, toggle in UI)

```text
Generated Text Answer
 ↓
Text-to-Speech — Sarvam Bulbul
 ↓
Audio Response (base64 → playable in browser)
```

### Requirements

-   **STT model:** Sarvam Saaras v3 — supports 23 Indian languages + English, auto language detection, works on short conversational audio clips.
-   **TTS model:** Sarvam Bulbul v3 — natural-sounding voice output in 11 languages (10 Indian + English), used only when the user enables "voice reply" in settings.
-   The transcript is shown to the user before submission (editable), so a misheard word can be corrected — this also gives the demo a visible "it heard me correctly" moment.
-   Voice queries follow the exact same retrieval/answer/citation pipeline as typed queries — voice is purely an input/output modality, not a separate logic path.
-   If STT confidence is low, the system asks the user to confirm or retype rather than silently guessing the question.
-   Voice messages are stored in the `messages` table with `input_mode = "voice"` and a link to the stored audio clip, so the conversation history remains fully auditable.

### Example API

```http
POST /api/v1/chat/voice
```

Request: multipart audio file + conversation_id.

Response:

```json
{
  "transcript": "इन सभी दस्तावेज़ों में पात्रता की शर्तें क्या हैं?",
  "detected_language": "hi-IN",
  "answer": "...",
  "sources": [ { "document": "policy.pdf", "page": 12, "section": "Eligibility" } ],
  "audio_reply_url": "https://.../reply_audio.mp3"
}
```

---

# 20. AI-Powered Response Generation

The LLM receives: user question (transcribed if voice), relevant conversation context, retrieved chunks, and source metadata. The system prompt enforces: use supplied evidence only, do not fabricate, state when evidence is insufficient, identify conflicting evidence, provide source/page references.

## 20A. Multilingual Response Generation (Sarvam AI)

-   **Model:** Sarvam-105B for Indic-language reasoning and answer generation when the user's query (typed or transcribed) is in an Indian language.
-   The system answers **in the language the user asked in**, even if the source document is in a different language — using Mayura/Sarvam-Translate to bridge retrieved English/Indic chunks into the response language, while keeping citations pointing to the original source document and page.
-   For English-only queries, the existing hosted LLM (Section 27) is used; routing between LLMs is based on detected query language.

---

# 21. Evidence-Based Responses

```json
{
  "answer": "The maximum entry age is 65 years.",
  "sources": [
    { "document": "Policy.pdf", "page": 12, "section": "Eligibility", "chunk_id": "abc123" }
  ]
}
```

---

# 22. Insufficient Information Handling

> I could not find sufficient information in the uploaded documents to answer this question.

The response should optionally identify which information was missing.

---

# 23. Conflicting Information Handling

```text
The uploaded documents contain conflicting information.

Policy A — Page 4: Maximum age: 60
Policy B — Page 8: Maximum age: 65
```

The system should not silently select one source without evidence.

---

# 24. Document Status

States: `UPLOADED, PROCESSING, COMPLETED, FAILED`.

Additional: `progress, current_stage, error_message`, plus **page-level status** (new) so a single failed page in a multi-page document does not mark the whole document as failed silently.

```json
{ "status": "PROCESSING", "progress": 65, "current_stage": "Generating embeddings" }
```

---

# 25. Backend API Requirements

## Authentication
```http
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

## Documents
```http
POST   /api/v1/documents/upload
GET    /api/v1/documents
GET    /api/v1/documents/{id}
GET    /api/v1/documents/{id}/status
DELETE /api/v1/documents/{id}
```

## Search
```http
POST /api/v1/search
```

## Chat
```http
POST /api/v1/chat
POST /api/v1/chat/voice
GET  /api/v1/chat/conversations
GET  /api/v1/chat/{conversation_id}
DELETE /api/v1/chat/{conversation_id}
```

## Evidence
```http
GET /api/v1/documents/{id}/pages/{page}
```

## Health
```http
GET /health
```

---

# 26. Data Model

## Users
```text
id, email, name, created_at
```
Authentication managed by Supabase Auth.

## Documents
```text
id, user_id, filename, file_type, file_size, storage_path,
status, total_pages, created_at, processed_at
```

## Document Pages
```text
id, document_id, page_number, raw_text, ocr_used, ocr_engine,
language, page_status, created_at
```

## Chunks
```text
id, document_id, page_id, chunk_index, content, language, metadata, created_at
```

## Conversations
```text
id, user_id, title, created_at
```

## Messages
```text
id, conversation_id, role, content, input_mode, language,
audio_url, created_at
```
`input_mode`: `text` | `voice`. `audio_url` populated for voice messages (user's spoken clip) and optionally for assistant spoken replies.

## Processing Jobs
```text
id, document_id, status, progress, current_stage, error_message, created_at, updated_at
```

---

# 27. Technology Requirements

## Frontend
- React, Vite, Tailwind CSS
- Browser MediaRecorder API for microphone capture

## Backend
- Python, FastAPI, Pydantic

## Database / Platform
- Supabase PostgreSQL, Supabase Auth, Supabase Storage

## Vector Search
- Qdrant

## Processing
- PyMuPDF (native PDF text)
- PaddleOCR (Latin-script OCR)
- Camelot (table extraction)
- python-docx (DOCX parsing)
- pandas (CSV parsing)
- **Sarvam Vision** (Indic-script OCR, table + layout extraction)

## AI
- BGE-M3 embeddings (multilingual)
- BGE Reranker
- LLM: hosted model (e.g. Llama/Qwen or equivalent) for English queries
- **Sarvam-105B** for Indic-language reasoning and answer generation
- **Mayura / Sarvam-Translate** for cross-lingual bridging

## Voice
- **Sarvam Saaras v3** — speech-to-text (23 languages)
- **Sarvam Bulbul v3** — text-to-speech (11 languages)

## Async Processing
- Redis, Celery (introduce after core MVP works synchronously — see Section 32)

## Deployment
- Docker, cloud deployment suitable for the chosen services

---

# 28. Backend Architecture

```text
                          React Frontend (text + mic input)
                                    |
                                    v
                              FastAPI API
                                    |
      +---------------+------------+------------+---------------+
      |               |            |            |               |
      v               v            v            v               v
  Supabase         Qdrant        Redis      Sarvam APIs      (LLM APIs)
      |               |            |        (STT/TTS/OCR/     
 +----+----+          |         Celery       Translate/LLM)
 |    |    |          |            |               |
 DB  Auth Storage     |            v               |
              Vector Search   Document Processing  |
                      |         /   |    |    \     |
                      |       PDF  OCR Tables Images|
                      |         \   |    |    /     |
                      |              |               |
                      +--------------+---------------+
                                     |
                                     v
                              RAG Pipeline
                                     |
                                     v
                                Reranker
                                     |
                                     v
                        Language Router (EN vs Indic)
                                 /       \
                                v         v
                        Hosted LLM    Sarvam-105B
                                 \       /
                                  v     v
                        Citation / Evidence Validation
                                     |
                                     v
                         Text Response + (optional) Bulbul TTS
                                     |
                                     v
                              API Response
```

---

# 29. Non-Functional Requirements

## Performance
- Upload API returns quickly without waiting for full document processing.
- Heavy processing is asynchronous.
- Retrieval is optimized for interactive chat.
- Vector search supports filtering.
- Voice transcription should complete within a few seconds for short clips (<30s) to keep the chat feel conversational.

## Reliability
- Failed processing jobs are marked `FAILED`; errors stored for debugging.
- Reprocessing is possible.
- Partial processing is not presented as completed (page-level status supports this).
- If Sarvam Vision job fails, fallback to PaddleOCR rather than failing the whole document.

## Security
- Users only access their own documents.
- Uploaded files and audio clips are not publicly exposed by default.
- Secrets stored in environment variables.
- Authenticated endpoints validate the user session.
- Database queries scoped to the authenticated user.

## Explainability
- Answers contain source references.
- Evidence maps to document/page/chunk.
- Conflicts are visible.
- Unsupported answers are clearly identified.
- Voice-transcribed queries show the transcript to the user for confirmation before being treated as ground truth.

---

# 30. Hackathon Demo Flow

```text
1. Login
       ↓
2. Upload 3–5 documents (include at least one regional-language scan)
       ↓
3. Processing progress shown, including OCR engine used per page
       ↓
4. Documents become searchable
       ↓
5. Ask a multi-source question BY VOICE (in a regional language)
       ↓
6. Transcript shown, backend retrieves relevant chunks across documents
       ↓
7. Reranker selects best evidence
       ↓
8. LLM (routed to Sarvam-105B) generates grounded response in the query language
       ↓
9. Sources/pages displayed; optional spoken reply plays
       ↓
10. Ask a typed follow-up question
       ↓
11. Context is maintained
       ↓
12. Demonstrate conflicting/insufficient information
```

---

# 31. Success Criteria

The MVP is considered complete when it can:

- Upload supported documents.
- Process normal PDFs.
- Process scanned/image documents through OCR, including Indic scripts via Sarvam Vision.
- Extract tables.
- Store page-level content and status.
- Chunk documents.
- Generate multilingual embeddings.
- Index chunks in Qdrant.
- Retrieve semantically relevant information, including across languages.
- Retrieve across multiple documents.
- Generate grounded AI answers, in the language the user asked in.
- Accept spoken questions and transcribe them accurately with user confirmation.
- Optionally reply with synthesized speech.
- Maintain conversation context across text and voice turns.
- Display document/page/section evidence.
- Avoid unsupported/fabricated answers.
- Identify conflicting information.
- Show document processing status.
- Enforce user-level document access.

---

# 32. MVP Priority

### P0 — Mandatory (trimmed for hackathon feasibility)
- FastAPI + Supabase (DB/Auth/Storage)
- Upload (synchronous or `BackgroundTasks`, not Celery yet)
- PDF extraction (PyMuPDF)
- DOCX / TXT / CSV parsing (python-docx, pandas)
- Basic OCR (PaddleOCR)
- Chunking
- Embeddings (BGE-M3)
- Qdrant semantic search
- LLM response with citations
- Chat context (text only)

### P1 — Strong Hackathon Features
- **Sarvam Vision integration for Indic-language OCR**
- **Voice query (Saaras STT) with transcript confirmation**
- Hybrid retrieval (dense + sparse fusion)
- Reranking
- Table extraction (Camelot)
- Conflict detection
- Processing progress UI
- Evidence viewer

### P2 — Future Enhancements
- **Voice reply (Bulbul TTS)**
- **Full cross-lingual query routing (Sarvam-105B + Mayura translation bridge)**
- Celery/Redis async processing at scale
- Advanced document layout understanding
- More file formats
- User/team sharing
- Advanced analytics
- Evaluation dashboard
- Feedback-based retrieval improvement
