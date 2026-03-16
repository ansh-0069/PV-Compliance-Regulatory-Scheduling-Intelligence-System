"""CAPA Workflow Service.

Implements the CAPA state machine:
  Open → Investigation → Corrective Action → Verification → Closed

Each transition is validated and recorded in an immutable audit trail.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundError, InvalidStateTransitionError
from app.models.capa import CAPA, CAPAAction, CAPAHistory
from app.schemas.capa import CAPAActionCreate, CAPACreate, CAPATransition

# ── Valid state transitions ───────────────────────────────────
VALID_TRANSITIONS: dict[str, set[str]] = {
    "Open":              {"Investigation"},
    "Investigation":     {"Open", "Corrective Action"},
    "Corrective Action": {"Investigation", "Verification"},
    "Verification":      {"Corrective Action", "Closed"},
    "Closed":            set(),  # terminal state
}


async def create_capa(db: AsyncSession, data: CAPACreate) -> CAPA:
    """Create a new CAPA and record the initial Open state."""
    capa = CAPA(**data.model_dump())
    db.add(capa)
    await db.flush()

    # Record initial history entry
    history = CAPAHistory(
        capa_id=capa.id,
        from_status="—",
        to_status="Open",
        changed_by=data.owner,
        comment="CAPA created",
    )
    db.add(history)
    await db.flush()
    await db.refresh(capa)
    return capa


async def transition_capa(
    db: AsyncSession,
    capa_id: uuid.UUID,
    data: CAPATransition,
) -> CAPA:
    """Validate and execute a CAPA state transition.

    Raises InvalidStateTransitionError if the requested transition
    is not permitted by the state machine.
    """
    result = await db.execute(select(CAPA).where(CAPA.id == capa_id))
    capa = result.scalar_one_or_none()
    if not capa:
        raise EntityNotFoundError("CAPA", str(capa_id))

    allowed = VALID_TRANSITIONS.get(capa.status, set())
    if data.to_status not in allowed:
        raise InvalidStateTransitionError(capa.status, data.to_status)

    # Record history
    history = CAPAHistory(
        capa_id=capa.id,
        from_status=capa.status,
        to_status=data.to_status,
        changed_by=data.changed_by,
        comment=data.comment,
    )
    db.add(history)

    # Apply transition
    capa.status = data.to_status
    await db.flush()
    await db.refresh(capa)
    return capa


async def add_capa_action(
    db: AsyncSession,
    capa_id: uuid.UUID,
    data: CAPAActionCreate,
) -> CAPAAction:
    """Add a corrective or preventive action to an existing CAPA."""
    result = await db.execute(select(CAPA).where(CAPA.id == capa_id))
    capa = result.scalar_one_or_none()
    if not capa:
        raise EntityNotFoundError("CAPA", str(capa_id))

    action = CAPAAction(capa_id=capa_id, **data.model_dump())
    db.add(action)
    await db.flush()
    await db.refresh(action)
    return action
