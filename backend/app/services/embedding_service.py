"""Multilingual dense embedding generation using BGE-M3."""

import hashlib
from typing import List, Optional
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_model_instance = None


class EmbeddingService:
    """Service generating multilingual dense embeddings for chunks and queries."""

    def __init__(self, model_name: Optional[str] = None) -> None:
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        self.dimension = settings.EMBEDDING_DIMENSION

    def _get_model(self):
        """Lazy load the sentence transformer embedding model."""
        global _model_instance
        if _model_instance is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info("Loading embedding model: %s", self.model_name)
                _model_instance = SentenceTransformer(self.model_name)
                logger.info("Embedding model loaded successfully")
            except Exception as exc:
                logger.warning("Could not load %s (%s); utilizing fallback encoder", self.model_name, str(exc))
                _model_instance = False
        return _model_instance

    def _deterministic_fallback_embed(self, text: str) -> List[float]:
        """Deterministic pseudo-embedding vector for test environments and offline fallbacks."""
        import math
        vec = []
        seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)
        for i in range(self.dimension):
            val = math.sin(seed + i)
            vec.append(val)
        # Normalize vector
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def _sync_embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Synchronous embedding generation worker."""
        if not texts:
            return []

        model = self._get_model()
        if model:
            try:
                embeddings = model.encode(texts, normalize_embeddings=True)
                return [
                    emb.tolist() if hasattr(emb, "tolist") else list(emb)
                    for emb in embeddings
                ]
            except Exception as exc:
                logger.error("Model inference failed, falling back: %s", str(exc))

        return [self._deterministic_fallback_embed(t) for t in texts]

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate normalized dense embeddings for a batch of text strings."""
        return await run_in_threadpool(self._sync_embed_batch, texts)

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate a single normalized dense embedding for a query or text chunk."""
        results = await self.generate_embeddings([text])
        return results[0] if results else [0.0] * self.dimension
