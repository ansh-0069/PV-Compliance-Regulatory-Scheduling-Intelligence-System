"""Deadline monitoring Celery tasks.

Periodically checks for overdue submissions and upcoming deadlines.
Sends alerts/reminders via internal notification system.
"""

from datetime import date, timedelta

from app.tasks.celery_app import celery


@celery.task(name="app.tasks.deadline_tasks.check_overdue_deadlines")
def check_overdue_deadlines():
    """Mark submissions whose due date has passed as Overdue.

    Runs hourly via Celery Beat. Uses a sync DB session.
    """
    from sqlalchemy import create_engine, update
    from sqlalchemy.orm import Session
    from app.config import settings
    from app.models.submission import Submission

    sync_url = settings.DATABASE_URL.replace("+asyncpg", "+psycopg2")
    engine = create_engine(sync_url)

    try:
        with Session(engine) as session:
            stmt = (
                update(Submission)
                .where(
                    Submission.status.in_(["Planned", "In-Progress"]),
                    Submission.submission_due < date.today(),
                )
                .values(status="Overdue")
            )
            result = session.execute(stmt)
            session.commit()
            return {"overdue_marked": result.rowcount}
    finally:
        engine.dispose()


@celery.task(name="app.tasks.deadline_tasks.send_deadline_reminders")
def send_deadline_reminders():
    """Send reminders for deadlines coming up in the next 7 days.

    In a production system this would integrate with an email/notification
    service. Currently logs the upcoming deadlines for demonstration.
    """
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from app.config import settings
    from app.models.submission import SubmissionDeadline

    sync_url = settings.DATABASE_URL.replace("+asyncpg", "+psycopg2")
    engine = create_engine(sync_url)

    try:
        with Session(engine) as session:
            upcoming = session.execute(
                select(SubmissionDeadline).where(
                    SubmissionDeadline.completed == False,
                    SubmissionDeadline.due_date.between(
                        date.today(),
                        date.today() + timedelta(days=7),
                    ),
                )
            ).scalars().all()

            reminders = []
            for dl in upcoming:
                reminders.append({
                    "deadline_id": str(dl.id),
                    "milestone": dl.milestone,
                    "due_date": str(dl.due_date),
                    "days_remaining": (dl.due_date - date.today()).days,
                })

            # In production: send emails / push notifications
            return {"reminders_sent": len(reminders), "details": reminders}
    finally:
        engine.dispose()
