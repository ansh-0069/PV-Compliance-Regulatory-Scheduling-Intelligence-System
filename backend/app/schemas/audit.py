"""Pydantic schemas for Audit Readiness scoring."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class AuditScoreRead(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID | None = None
    score_date: date
    overall_score: float = Field(..., ge=0, le=100)
    dimension_scores: dict | None = None
    findings_summary: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditScoreHistory(BaseModel):
    items: list[AuditScoreRead]
    total: int


class AuditRecalculateResponse(BaseModel):
    message: str = "Audit score recalculation triggered"
    score: AuditScoreRead | None = None
