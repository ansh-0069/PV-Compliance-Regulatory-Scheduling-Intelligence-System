"""FastAPI application factory.

This is the main entry point for the PV Compliance API.
Uvicorn targets this module: ``uvicorn app.main:app``
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown hooks."""
    setup_logging()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="PV Compliance & Regulatory Scheduling Intelligence System",
        description=(
            "Enterprise pharmacovigilance operations platform for managing "
            "regulatory submissions, QC validation, CAPA lifecycle, audit readiness, "
            "and an AI Compliance Copilot."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception handlers ────────────────────────────
    register_exception_handlers(app)

    # ── Routes ────────────────────────────────────────
    app.include_router(api_router)

    # ── Health check ──────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health():
        return {"status": "healthy", "service": "pv-compliance-api"}

    return app


app = create_app()
