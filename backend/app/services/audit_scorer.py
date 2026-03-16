"""Audit Readiness Scoring Service.

Aggregates compliance indicators across submissions, QC checks, and CAPAs
to produce a 0-100 audit readiness score broken down by dimension.
"""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditScore
from app.models.capa import CAPA
from app.models.qc import QCCheck
from app.models.submission import Submission

# ── Scoring weights ───────────────────────────────────
WEIGHTS = {
    "submission_timeliness": 0.30,
    "qc_pass_rate":          0.25,
    "capa_closure_rate":     0.25,
    "capa_aging":            0.20,
}


async def recalculate_audit_score(
    db: AsyncSession,
    product_id: uuid.UUID | None = None,
) -> AuditScore:
    """Calculate and persist a new audit readiness score.

    Dimensions:
    - submission_timeliness : % of submissions not overdue
    - qc_pass_rate          : % of QC checks that passed
    - capa_closure_rate     : % of CAPAs that are Closed
    - capa_aging            : inverse of average open-CAPA age in days
    """

    # ── Submission timeliness ─────────────────────────
    sub_q = select(func.count(Submission.id))
    overdue_q = select(func.count(Submission.id)).where(Submission.status == "Overdue")
    if product_id:
        sub_q = sub_q.where(Submission.product_id == product_id)
        overdue_q = overdue_q.where(Submission.product_id == product_id)

    total_subs = (await db.execute(sub_q)).scalar() or 0
    overdue_subs = (await db.execute(overdue_q)).scalar() or 0
    timeliness = ((total_subs - overdue_subs) / total_subs * 100) if total_subs else 100.0

    # ── QC pass rate ──────────────────────────────────
    qc_total_q = select(func.count(QCCheck.id)).where(QCCheck.status.in_(["Passed", "Failed"]))
    qc_pass_q = select(func.count(QCCheck.id)).where(QCCheck.status == "Passed")
    qc_total = (await db.execute(qc_total_q)).scalar() or 0
    qc_passed = (await db.execute(qc_pass_q)).scalar() or 0
    qc_rate = (qc_passed / qc_total * 100) if qc_total else 100.0

    # ── CAPA closure rate ─────────────────────────────
    capa_total = (await db.execute(select(func.count(CAPA.id)))).scalar() or 0
    capa_closed = (await db.execute(
        select(func.count(CAPA.id)).where(CAPA.status == "Closed")
    )).scalar() or 0
    closure_rate = (capa_closed / capa_total * 100) if capa_total else 100.0

    # ── CAPA aging ────────────────────────────────────
    open_capas = (await db.execute(
        select(CAPA).where(CAPA.status != "Closed")
    )).scalars().all()
    if open_capas:
        avg_age = sum(
            (datetime.now(timezone.utc) - c.created_at).days for c in open_capas
        ) / len(open_capas)
        aging_score = max(0, 100 - avg_age * 2)  # lose 2 pts per day
    else:
        aging_score = 100.0

    # ── Weighted overall ──────────────────────────────
    dimension_scores = {
        "submission_timeliness": round(timeliness, 1),
        "qc_pass_rate": round(qc_rate, 1),
        "capa_closure_rate": round(closure_rate, 1),
        "capa_aging": round(aging_score, 1),
    }

    overall = sum(
        dimension_scores[dim] * weight
        for dim, weight in WEIGHTS.items()
    )

    score = AuditScore(
        product_id=product_id,
        score_date=date.today(),
        overall_score=round(overall, 1),
        dimension_scores=dimension_scores,
        findings_summary={
            "total_submissions": total_subs,
            "overdue_submissions": overdue_subs,
            "qc_checks_evaluated": qc_total,
            "open_capas": len(open_capas),
        },
    )
    db.add(score)
    await db.flush()
    await db.refresh(score)
    return score
