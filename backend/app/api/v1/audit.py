"""Audit readiness score endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.database import get_db
from app.models.audit import AuditScore
from app.models.user import User
from app.schemas.audit import AuditRecalculateResponse, AuditScoreHistory, AuditScoreRead
from app.services.audit_scorer import recalculate_audit_score

router = APIRouter(prefix="/audit", tags=["Audit Readiness"])


@router.get("/score", response_model=AuditScoreRead | None)
async def get_current_score(
    product_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Get the latest audit readiness score (org-wide or per-product)."""
    query = select(AuditScore).order_by(AuditScore.score_date.desc()).limit(1)
    if product_id:
        query = query.where(AuditScore.product_id == product_id)
    else:
        query = query.where(AuditScore.product_id.is_(None))
    result = await db.execute(query)
    return result.scalar_one_or_none()


@router.get("/score/history", response_model=AuditScoreHistory)
async def get_score_history(
    product_id: uuid.UUID | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Get audit score trend over time."""
    query = select(AuditScore).order_by(AuditScore.score_date.desc())
    if product_id:
        query = query.where(AuditScore.product_id == product_id)
    else:
        query = query.where(AuditScore.product_id.is_(None))
    result = await db.execute(query.offset(offset).limit(limit))
    items = result.scalars().all()
    return AuditScoreHistory(items=items, total=len(items))


@router.post("/score/recalculate", response_model=AuditRecalculateResponse)
async def trigger_recalculation(
    product_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("Admin", "QA")),
):
    """Trigger an immediate audit score recalculation."""
    score = await recalculate_audit_score(db, product_id)
    return AuditRecalculateResponse(
        message="Audit score recalculated successfully",
        score=score,
    )
