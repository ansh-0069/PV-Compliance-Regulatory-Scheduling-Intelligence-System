"""CAPA lifecycle management endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.core.exceptions import EntityNotFoundError
from app.database import get_db
from app.models.capa import CAPA, CAPAHistory
from app.models.user import User
from app.schemas.capa import (
    CAPAActionCreate,
    CAPAActionRead,
    CAPACreate,
    CAPAHistoryRead,
    CAPAList,
    CAPARead,
    CAPATransition,
)
from app.services.capa_workflow import add_capa_action, create_capa, transition_capa

router = APIRouter(prefix="/capas", tags=["CAPAs"])


@router.get("", response_model=CAPAList)
async def list_capas(
    status: str | None = None,
    priority: str | None = None,
    owner: str | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """List CAPAs with optional filters."""
    query = select(CAPA)
    count_query = select(func.count(CAPA.id))
    if status:
        query = query.where(CAPA.status == status)
        count_query = count_query.where(CAPA.status == status)
    if priority:
        query = query.where(CAPA.priority == priority)
        count_query = count_query.where(CAPA.priority == priority)
    if owner:
        query = query.where(CAPA.owner.ilike(f"%{owner}%"))
        count_query = count_query.where(CAPA.owner.ilike(f"%{owner}%"))
    total = (await db.execute(count_query)).scalar() or 0
    result = await db.execute(query.offset(offset).limit(limit).order_by(CAPA.created_at.desc()))
    return CAPAList(items=result.scalars().all(), total=total)


@router.post("", response_model=CAPARead, status_code=201)
async def create_capa_endpoint(
    body: CAPACreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("Admin", "PV-Officer", "QA")),
):
    """Create a new CAPA."""
    return await create_capa(db, body)


@router.patch("/{capa_id}/transition", response_model=CAPARead)
async def transition_capa_endpoint(
    capa_id: uuid.UUID,
    body: CAPATransition,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("Admin", "PV-Officer", "QA")),
):
    """Advance CAPA through its lifecycle states."""
    return await transition_capa(db, capa_id, body)


@router.get("/{capa_id}/history", response_model=list[CAPAHistoryRead])
async def get_capa_history(
    capa_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Get full audit trail for a CAPA."""
    result = await db.execute(
        select(CAPAHistory)
        .where(CAPAHistory.capa_id == capa_id)
        .order_by(CAPAHistory.changed_at)
    )
    return result.scalars().all()


@router.post("/{capa_id}/actions", response_model=CAPAActionRead, status_code=201)
async def add_action(
    capa_id: uuid.UUID,
    body: CAPAActionCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("Admin", "PV-Officer", "QA")),
):
    """Add a corrective or preventive action to a CAPA."""
    return await add_capa_action(db, capa_id, body)
