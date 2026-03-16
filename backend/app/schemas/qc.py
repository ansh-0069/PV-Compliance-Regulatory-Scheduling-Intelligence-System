"""Pydantic schemas for QC check operations."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class QCFindingRead(BaseModel):
    id: uuid.UUID
    severity: str
    section: str | None = None
    description: str
    recommendation: str | None = None

    model_config = {"from_attributes": True}


class QCCheckRead(BaseModel):
    id: uuid.UUID
    submission_id: uuid.UUID
    file_key: str
    status: str
    overall_score: float | None = None
    metadata_: dict | None = Field(None, alias="metadata")
    created_at: datetime
    findings: list[QCFindingRead] = []

    model_config = {"from_attributes": True, "populate_by_name": True}


class QCCheckList(BaseModel):
    items: list[QCCheckRead]
    total: int


class QCCheckUploadResponse(BaseModel):
    """Returned immediately after upload — task runs async."""
    qc_check_id: uuid.UUID
    status: str = "Pending"
    message: str = "QC check queued for processing"
