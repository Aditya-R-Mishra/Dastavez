# Dastavez Backend - Document Intelligence & Multi-Source Search

FastAPI backend powering the Dastavez Document Intelligence and RAG platform.

## Architecture Discipline

- **Strict Layering**: `router` → `service` → `repository` → `external client`.
  - Routers never touch the database or external APIs directly.
  - Services never import FastAPI request/response objects.
  - Repositories never contain business logic.
- **No God Files**: All modules kept modular, single-responsibility, and strictly under ~300 lines.
- **Unified Configuration**: Centralized `app/core/config.py` using `pydantic-settings`.
- **Structured Error Handling**: Custom domain exceptions in `app/core/exceptions.py` mapped to HTTP responses.
- **Structured Logging**: Context-aware logging in `app/core/logging.py` tracing `document_id` and `job_id`.
- **Interfaces for Integrations**: Thin clients isolated under `app/integrations/` behind interfaces (`BaseOCREngine`, `BaseLLMProvider`).

---

## API Endpoints Implemented

### Authentication (FR-01)
- `POST /api/v1/auth/register`: Register user with Supabase Auth
- `POST /api/v1/auth/login`: Authenticate and obtain JWT
- `GET /api/v1/auth/me`: Fetch authenticated user profile

### Document Management & Ingestion (P0)
- `POST /api/v1/documents/upload`: Validate, store in Supabase Storage, and trigger background pipeline
- `GET /api/v1/documents`: List user documents with pagination
- `GET /api/v1/documents/{id}`: Fetch document metadata and page count
- `GET /api/v1/documents/{id}/status`: Track real-time progress (0–100%) and pipeline stage
- `DELETE /api/v1/documents/{id}`: Delete storage files, Qdrant vectors, and DB records
- `GET /api/v1/documents/{id}/pages/{page}`: Inspect raw text, OCR engine used, and page status

### Search & Retrieval (P0)
- `POST /api/v1/search`: Dense multilingual vector retrieval via BGE-M3 & Qdrant with document filtering

### Multi-turn Grounded Chat (P0)
- `POST /api/v1/chat`: Multi-turn conversational RAG with strict evidence grounding and structured citations
- `GET /api/v1/chat/conversations`: List user conversation threads
- `GET /api/v1/chat/{conversation_id}`: Fetch conversation thread with chronological message history
- `DELETE /api/v1/chat/{conversation_id}`: Delete conversation thread

---

## Getting Started

### 1. Prerequisites
- Python 3.12+
- Docker & Docker Compose (for local Qdrant)
- Supabase project (URL, keys, JWT secret)

### 2. Environment Setup
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 3. Database Migration
Apply the database schema to your Supabase PostgreSQL instance:
```bash
# Execute backend/supabase/migrations/20260926000000_initial_schema.sql in Supabase SQL editor
```

### 4. Running Locally
Start local Qdrant vector database:
```bash
docker-compose up -d qdrant
```

Run FastAPI server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/health`

### 5. Running Tests
Run the comprehensive test suite with pytest:
```bash
PYTHONPATH=. pytest -v
```
