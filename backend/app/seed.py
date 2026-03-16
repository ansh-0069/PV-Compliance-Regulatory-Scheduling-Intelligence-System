"""Seed data script — populates the database with realistic demo data.

Usage:
    python -m app.seed
"""

import asyncio
import uuid
from datetime import date, timedelta

from app.config import settings
from app.core.security import hash_password
from app.database import Base, engine, async_session
from app.models.user import User
from app.models.product import Product
from app.models.submission import Submission, SubmissionDeadline
from app.models.capa import CAPA, CAPAAction, CAPAHistory, RootCauseCategory
from app.models.qc import QCCheck, QCFinding
from app.models.audit import AuditScore


async def seed():
    """Drop and re-create all tables, then populate with seed data."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        # ── Users ─────────────────────────────────────
        users = [
            User(email="admin@pvcompli.com", full_name="Sarah Chen", role="Admin", password_hash=hash_password("admin123")),
            User(email="officer@pvcompli.com", full_name="James Rodriguez", role="PV-Officer", password_hash=hash_password("officer123")),
            User(email="qa@pvcompli.com", full_name="Priya Sharma", role="QA", password_hash=hash_password("qa123")),
            User(email="viewer@pvcompli.com", full_name="Michael Brown", role="Viewer", password_hash=hash_password("viewer123")),
        ]
        db.add_all(users)
        await db.flush()

        # ── Root Cause Categories ─────────────────────
        rcc = [
            RootCauseCategory(code="RC-001", name="Process Deviation"),
            RootCauseCategory(code="RC-002", name="System Failure"),
            RootCauseCategory(code="RC-003", name="Human Error"),
            RootCauseCategory(code="RC-004", name="Training Gap"),
            RootCauseCategory(code="RC-005", name="Data Integrity Issue"),
        ]
        db.add_all(rcc)
        await db.flush()

        # ── Products ──────────────────────────────────
        products = [
            Product(name="Xarelto", active_substance="Rivaroxaban", mah="Bayer AG", ibd=date(2008, 9, 15)),
            Product(name="Eylea", active_substance="Aflibercept", mah="Bayer AG", ibd=date(2011, 11, 18)),
            Product(name="Jardiance", active_substance="Empagliflozin", mah="Boehringer Ingelheim", ibd=date(2014, 8, 1)),
        ]
        db.add_all(products)
        await db.flush()

        # ── Submissions ──────────────────────────────
        today = date.today()
        submissions = [
            Submission(product_id=products[0].id, type="PSUR", cycle="PSUR-24", data_lock_point=today - timedelta(days=30), submission_due=today + timedelta(days=60), status="In-Progress", authority="EMA"),
            Submission(product_id=products[0].id, type="PSUR", cycle="PSUR-25", data_lock_point=today + timedelta(days=150), submission_due=today + timedelta(days=240), status="Planned", authority="EMA"),
            Submission(product_id=products[1].id, type="DSUR", cycle="DSUR-08", data_lock_point=today - timedelta(days=60), submission_due=today - timedelta(days=5), status="Overdue", authority="FDA"),
            Submission(product_id=products[2].id, type="RMP", cycle="RMP-03", data_lock_point=today + timedelta(days=30), submission_due=today + timedelta(days=120), status="Planned", authority="EMA"),
        ]
        db.add_all(submissions)
        await db.flush()

        # ── Milestones ────────────────────────────────
        for sub in submissions:
            for milestone, offset in [("DLP", 90), ("Draft", 60), ("QC", 30), ("Filing", 0)]:
                dl = SubmissionDeadline(
                    submission_id=sub.id,
                    milestone=milestone,
                    due_date=sub.submission_due - timedelta(days=offset),
                    completed=(offset > 30 and sub.status == "In-Progress"),
                )
                db.add(dl)

        # ── QC Checks ────────────────────────────────
        qc1 = QCCheck(submission_id=submissions[0].id, file_key="qc/sample/report_section_3.pdf", status="Passed", overall_score=94.2)
        qc2 = QCCheck(submission_id=submissions[2].id, file_key="qc/sample/dsur_section_7.pdf", status="Failed", overall_score=58.1)
        db.add_all([qc1, qc2])
        await db.flush()

        db.add_all([
            QCFinding(qc_check_id=qc1.id, severity="Minor", section="Section 3.2", description="Minor formatting inconsistency in table headers", recommendation="Standardise header capitalisation"),
            QCFinding(qc_check_id=qc2.id, severity="Critical", section="Section 7.1", description="Missing adverse event summary data for Q3 reporting period", recommendation="Retrieve AE data from signal detection database"),
            QCFinding(qc_check_id=qc2.id, severity="Major", section="Section 7.3", description="Cross-reference mismatch between line listing and aggregate table", recommendation="Reconcile case counts with validated line listing"),
        ])

        # ── CAPAs ─────────────────────────────────────
        capa1 = CAPA(submission_id=submissions[2].id, title="Missing AE data in DSUR-08", description="Critical adverse event data for Q3 was not included in DSUR Section 7.1", status="Investigation", priority="Critical", owner="James Rodriguez", target_closure=today + timedelta(days=30), root_cause_category_id=rcc[4].id)
        capa2 = CAPA(title="Late PSUR submission process improvement", description="Recurring delays in PSUR draft completion due to manual data extraction", status="Corrective Action", priority="High", owner="Priya Sharma", target_closure=today + timedelta(days=45), root_cause_category_id=rcc[0].id)
        capa3 = CAPA(title="QC reviewer training programme", description="Inconsistent QC review outcomes across team members", status="Open", priority="Medium", owner="Sarah Chen", target_closure=today + timedelta(days=60), root_cause_category_id=rcc[3].id)
        db.add_all([capa1, capa2, capa3])
        await db.flush()

        # CAPA History
        db.add_all([
            CAPAHistory(capa_id=capa1.id, from_status="—", to_status="Open", changed_by="James Rodriguez", comment="CAPA created"),
            CAPAHistory(capa_id=capa1.id, from_status="Open", to_status="Investigation", changed_by="James Rodriguez", comment="Root cause analysis initiated"),
            CAPAHistory(capa_id=capa2.id, from_status="—", to_status="Open", changed_by="Priya Sharma", comment="CAPA created"),
            CAPAHistory(capa_id=capa2.id, from_status="Open", to_status="Investigation", changed_by="Priya Sharma", comment="Reviewed historical data"),
            CAPAHistory(capa_id=capa2.id, from_status="Investigation", to_status="Corrective Action", changed_by="Priya Sharma", comment="Automation solution identified"),
            CAPAHistory(capa_id=capa3.id, from_status="—", to_status="Open", changed_by="Sarah Chen", comment="CAPA created"),
        ])

        # CAPA Actions
        db.add_all([
            CAPAAction(capa_id=capa1.id, action_type="Corrective", description="Retrieve missing Q3 AE data and update DSUR", assignee="James Rodriguez", due_date=today + timedelta(days=7), status="In-Progress"),
            CAPAAction(capa_id=capa2.id, action_type="Preventive", description="Implement automated data extraction pipeline", assignee="Priya Sharma", due_date=today + timedelta(days=30), status="Pending"),
            CAPAAction(capa_id=capa2.id, action_type="Corrective", description="Create standard operating procedure for PSUR timeline management", assignee="Sarah Chen", due_date=today + timedelta(days=14), status="In-Progress"),
        ])

        # ── Audit Score ───────────────────────────────
        db.add(AuditScore(
            product_id=None,
            score_date=today,
            overall_score=73.8,
            dimension_scores={
                "submission_timeliness": 75.0,
                "qc_pass_rate": 50.0,
                "capa_closure_rate": 0.0,
                "capa_aging": 92.0,
            },
            findings_summary={
                "total_submissions": 4,
                "overdue_submissions": 1,
                "qc_checks_evaluated": 2,
                "open_capas": 3,
            },
        ))

        await db.commit()
        print("✅ Seed data loaded successfully!")
        print(f"   Users:       {len(users)}")
        print(f"   Products:    {len(products)}")
        print(f"   Submissions: {len(submissions)}")
        print(f"   QC Checks:   2")
        print(f"   CAPAs:       3")
        print(f"   Audit Score: 73.8%")


if __name__ == "__main__":
    asyncio.run(seed())
