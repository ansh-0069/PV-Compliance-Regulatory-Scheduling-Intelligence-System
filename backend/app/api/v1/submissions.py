"""Submission endpoints: CRUD + schedule generation."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.core.exceptions import EntityNotFoundError
from app.database import get_db
from app.models.submission import Submission, SubmissionDeadline
from app.models.user import User
from app.schemas.submission import (
    DeadlineRead,
    GenerateScheduleRequest,
    SubmissionCreate,
    SubmissionList,
    SubmissionRead,
    SubmissionUpdate,
)
from app.services.scheduler import generate_submission_schedule

router = APIRouter(prefix="/submissions", tags=["Submissions"])


@router.get("", response_model=SubmissionList)
async def list_submissions(
    product_id: uuid.UUID | None = None,
    status: str | None = None,
    type: str | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """List submissions with filters."""
    query = select(Submission)
    count_query = select(func.count(Submission.id))
    if product_id:
        query = query.where(Submission.product_id == product_id)
        count_query = count_query.where(Submission.product_id == product_id)
    if status:
        query = query.where(Submission.status == status)
        count_query = count_query.where(Submission.status == status)
    if type:
        query = query.where(Submission.type == type)
        count_query = count_query.where(Submission.type == type)
    total = (await db.execute(count_query)).scalar() or 0
    result = await db.execute(query.offset(offset).limit(limit).order_by(Submission.submission_due))
    return SubmissionList(items=result.scalars().all(), total=total)


@router.post("", response_model=SubmissionRead, status_code=201)
async def create_submission(
    body: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("Admin", "PV-Officer")),
):
    """Create a single submission cycle."""
    submission = Submission(**body.model_dump())
    db.add(submission)
    await db.flush()
    await db.refresh(submission)
    return submission


@router.patch("/{submission_id}", response_model=SubmissionRead)
async def update_submission(
    submission_id: uuid.UUID,
    body: SubmissionUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("Admin", "PV-Officer")),
):
    """Update submission status or dates."""
    result = await db.execute(select(Submission).where(Submission.id == submission_id))
    submission = result.scalar_one_or_none()
    if not submission:
        raise EntityNotFoundError("Submission", str(submission_id))
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(submission, field, value)
    await db.flush()
    await db.refresh(submission)
    return submission


@router.get("/{submission_id}/deadlines", response_model=list[DeadlineRead])
async def get_deadlines(
    submission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Get milestone deadlines for a submission."""
    result = await db.execute(
        select(SubmissionDeadline)
        .where(SubmissionDeadline.submission_id == submission_id)
        .order_by(SubmissionDeadline.due_date)
    )
    return result.scalars().all()


@router.post("/generate-schedule", response_model=list[SubmissionRead], status_code=201)
async def generate_schedule(
    body: GenerateScheduleRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("Admin", "PV-Officer")),
):
    """Auto-generate submission cycles + milestones from IBD."""
    submissions = await generate_submission_schedule(db, body)
    return submissions
