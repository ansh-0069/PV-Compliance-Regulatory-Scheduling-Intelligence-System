"""Regulatory Submission Scheduler Service.

Generates submission cycles (PSUR/DSUR/RMP) and milestones based on
a product's International Birth Date (IBD) and regulatory authority rules.
"""

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EntityNotFoundError
from app.models.product import Product
from app.models.submission import Submission, SubmissionDeadline
from app.schemas.submission import GenerateScheduleRequest

# ── Cycle length rules (months) per report type and authority ─────
CYCLE_MONTHS: dict[str, dict[str, int]] = {
    "PSUR": {"EMA": 6, "FDA": 12, "PMDA": 6},
    "DSUR": {"EMA": 12, "FDA": 12, "PMDA": 12},
    "RMP":  {"EMA": 12, "FDA": 12, "PMDA": 12},
}

# Days before submission_due for each milestone
MILESTONE_OFFSETS: dict[str, int] = {
    "DLP":    90,   # Data Lock Point: 90 days before due
    "Draft":  60,   # Draft completion: 60 days before due
    "QC":     30,   # QC review: 30 days before due
    "Filing": 0,    # Filing = due date itself
}


def _add_months(start: date, months: int) -> date:
    """Add months to a date, clamping to valid day."""
    month = start.month - 1 + months
    year = start.year + month // 12
    month = month % 12 + 1
    day = min(start.day, 28)  # safe clamping
    return date(year, month, day)


async def generate_submission_schedule(
    db: AsyncSession,
    request: GenerateScheduleRequest,
) -> list[Submission]:
    """Auto-generate N submission cycles with milestones from the product's IBD.

    1. Looks up the product to find its IBD.
    2. Computes DLP and due dates for each cycle.
    3. Creates Submission + SubmissionDeadline rows.
    """
    result = await db.execute(select(Product).where(Product.id == request.product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise EntityNotFoundError("Product", str(request.product_id))

    cycle_months = CYCLE_MONTHS.get(request.type, {}).get(request.authority, 6)
    submissions: list[Submission] = []

    for i in range(1, request.num_cycles + 1):
        dlp = _add_months(product.ibd, cycle_months * i)
        due = dlp + timedelta(days=90)  # 90-day clock from DLP

        submission = Submission(
            product_id=request.product_id,
            type=request.type,
            cycle=f"{request.type}-{i:02d}",
            data_lock_point=dlp,
            submission_due=due,
            authority=request.authority,
            status="Planned",
        )
        db.add(submission)
        await db.flush()
        await db.refresh(submission)

        # Create milestones
        for milestone, offset_days in MILESTONE_OFFSETS.items():
            deadline = SubmissionDeadline(
                submission_id=submission.id,
                milestone=milestone,
                due_date=due - timedelta(days=offset_days),
            )
            db.add(deadline)

        submissions.append(submission)

    await db.flush()
    for s in submissions:
        await db.refresh(s)
    return submissions
