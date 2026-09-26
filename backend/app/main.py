"""FastAPI application entry point, lifecycle configuration, and routing."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.schemas.common import HealthResponse

# Initialize structured logging
setup_logging(debug=settings.DEBUG)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager handling application startup and shutdown hooks."""
    logger.info("Starting up %s in %s environment", settings.APP_NAME, settings.APP_ENV)
    yield
    logger.info("Shutting down %s", settings.APP_NAME)


def create_application() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    app = FastAPI(
        title=settings.APP_NAME,
        version="2.0.0",
        description="FastAPI backend for Dastavez Document Intelligence & Multi-Source Search",
        lifespan=lifespan,
    )

    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register custom domain exception handlers
    register_exception_handlers(app)

    # Register core health check endpoint
    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    async def health_check() -> HealthResponse:
        """Health check endpoint to verify service liveness."""
        return HealthResponse(
            status="healthy",
            version="2.0.0",
            environment=settings.APP_ENV,
        )

    # Register aggregated API v1 routes
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)

    return app


app = create_application()
