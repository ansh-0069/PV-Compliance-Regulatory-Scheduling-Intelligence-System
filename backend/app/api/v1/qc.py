"""QC check endpoints: upload, results, listing."""

import uuid

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.core.exceptions import EntityNotFoundError
from app.database import get_db
from app.models.qc import QCCheck
from app.models.user import User
from app.schemas.qc import QCCheckList, QCCheckRead, QCCheckUploadResponse
from app.services.qc_engine import upload_and_enqueue_qc

router = APIRouter(prefix="/qc", tags=["QC Checks"])


@router.post("/check", response_model=QCCheckUploadResponse, status_code=202)
async def upload_for_qc(
    submission_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("Admin", "PV-Officer", "QA")),
):
    """Upload a report section for AI-powered QC.

    The file is stored in MinIO and a Celery task is enqueued for
    asynchronous analysis. Returns immediately with a tracking ID.
    """
    result = await upload_and_enqueue_qc(db, submission_id, file)
    return result


@router.get("/results/{qc_check_id}", response_model=QCCheckRead)
async def get_qc_result(
    qc_check_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Get QC check result and findings."""
    result = await db.execute(select(QCCheck).where(QCCheck.id == qc_check_id))
    qc = result.scalar_one_or_none()
    if not qc:
        raise EntityNotFoundError("QCCheck", str(qc_check_id))
    return qc


@router.get("/results", response_model=QCCheckList)
async def list_qc_checks(
    submission_id: uuid.UUID | None = None,
    status: str | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """List QC checks with optional filters."""
    query = select(QCCheck)
    count_query = select(func.count(QCCheck.id))
    if submission_id:
        query = query.where(QCCheck.submission_id == submission_id)
        count_query = count_query.where(QCCheck.submission_id == submission_id)
    if status:
        query = query.where(QCCheck.status == status)
        count_query = count_query.where(QCCheck.status == status)
    total = (await db.execute(count_query)).scalar() or 0
    result = await db.execute(query.offset(offset).limit(limit).order_by(QCCheck.created_at.desc()))
    return QCCheckList(items=result.scalars().all(), total=total)
