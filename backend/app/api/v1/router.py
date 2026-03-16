"""Aggregated v1 API router — mounts all resource routers under /api/v1."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.products import router as products_router
from app.api.v1.submissions import router as submissions_router
from app.api.v1.qc import router as qc_router
from app.api.v1.capas import router as capas_router
from app.api.v1.audit import router as audit_router
from app.api.v1.copilot import router as copilot_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(products_router)
api_router.include_router(submissions_router)
api_router.include_router(qc_router)
api_router.include_router(capas_router)
api_router.include_router(audit_router)
api_router.include_router(copilot_router)
