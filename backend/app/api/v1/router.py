"""Aggregated API v1 router combining all domain sub-routers."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.documents import router as documents_router
from app.api.v1.evidence import router as evidence_router
from app.api.v1.search import router as search_router

api_v1_router = APIRouter()

# Include all sub-routers
api_v1_router.include_router(auth_router)
api_v1_router.include_router(documents_router)
api_v1_router.include_router(search_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(evidence_router)
