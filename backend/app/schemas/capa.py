"""Pydantic schemas for CAPA lifecycle management."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


# ── CAPA Actions ──────────────────────────────────────

class CAPAActionCreate(BaseModel):
    action_type: str = Field(..., pattern="^(Corrective|Preventive)$")
    description: str
    assignee: str
    due_date: date


class CAPAActionRead(BaseModel):
    id: uuid.UUID
    action_type: str
    description: str
    assignee: str
    due_date: date
    status: str
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


# ── CAPA History ──────────────────────────────────────

class CAPAHistoryRead(BaseModel):
    id: uuid.UUID
    from_status: str
    to_status: str
    changed_by: str
    comment: str | None = None
    changed_at: datetime

    model_config = {"from_attributes": True}


# ── CAPA ──────────────────────────────────────────────

class CAPACreate(BaseModel):
    submission_id: uuid.UUID | None = None
    title: str = Field(..., max_length=500)
    description: str
    priority: str = Field(default="Medium", pattern="^(Critical|High|Medium|Low)$")
    owner: str
    target_closure: date | None = None
    root_cause_category_id: uuid.UUID | None = None


class CAPATransition(BaseModel):
    """Request body for advancing CAPA through its lifecycle."""
    to_status: str = Field(
        ...,
        pattern="^(Open|Investigation|Corrective Action|Verification|Closed)$",
        examples=["Investigation"],
    )
    changed_by: str
    comment: str | None = None


class CAPARead(BaseModel):
    id: uuid.UUID
    submission_id: uuid.UUID | None = None
    title: str
    description: str
    status: str
    priority: str
    owner: str
    target_closure: date | None = None
    root_cause_category_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
    actions: list[CAPAActionRead] = []

    model_config = {"from_attributes": True}


class CAPAList(BaseModel):
    items: list[CAPARead]
    total: int
