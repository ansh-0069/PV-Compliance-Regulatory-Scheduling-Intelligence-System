"""Pydantic schemas for Submission and Deadline operations."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


# ── Submission Deadlines ──────────────────────────────

class DeadlineBase(BaseModel):
    milestone: str = Field(..., max_length=50, examples=["DLP"])
    due_date: date


class DeadlineRead(DeadlineBase):
    id: uuid.UUID
    completed: bool
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


# ── Submissions ──────────────────────────────────────

class SubmissionBase(BaseModel):
    product_id: uuid.UUID
    type: str = Field(..., pattern="^(PSUR|DSUR|RMP)$", examples=["PSUR"])
    cycle: str = Field(..., max_length=50, examples=["PSUR-12"])
    data_lock_point: date
    submission_due: date
    authority: str = Field(default="EMA", max_length=50)


class SubmissionCreate(SubmissionBase):
    pass


class SubmissionUpdate(BaseModel):
    status: str | None = Field(None, pattern="^(Planned|In-Progress|Submitted|Overdue)$")
    submission_due: date | None = None
    authority: str | None = None


class SubmissionRead(SubmissionBase):
    id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime
    deadlines: list[DeadlineRead] = []

    model_config = {"from_attributes": True}


class SubmissionList(BaseModel):
    items: list[SubmissionRead]
    total: int


class GenerateScheduleRequest(BaseModel):
    """Request body for auto-generating submission schedule from IBD."""
    product_id: uuid.UUID
    type: str = Field(..., pattern="^(PSUR|DSUR|RMP)$")
    num_cycles: int = Field(default=4, ge=1, le=20)
    authority: str = Field(default="EMA")
