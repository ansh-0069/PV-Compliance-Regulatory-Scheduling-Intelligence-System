"""Celery application instance and beat schedule configuration.

This module is the target for celery CLI:
  celery -A app.tasks.celery_app worker --loglevel=info
  celery -A app.tasks.celery_app beat  --loglevel=info
"""

from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery = Celery(
    "pv_compliance",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.qc_tasks",
        "app.tasks.deadline_tasks",
        "app.tasks.scoring_tasks",
    ],
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_routes={
        "app.tasks.qc_tasks.*": {"queue": "qc"},
        "app.tasks.scoring_tasks.*": {"queue": "scoring"},
        "app.tasks.deadline_tasks.*": {"queue": "default"},
    },
)

# ── Periodic tasks (Celery Beat) ──────────────────────
celery.conf.beat_schedule = {
    "check-overdue-deadlines-hourly": {
        "task": "app.tasks.deadline_tasks.check_overdue_deadlines",
        "schedule": crontab(minute=0),  # Every hour
    },
    "recalculate-audit-scores-daily": {
        "task": "app.tasks.scoring_tasks.recalculate_all_scores",
        "schedule": crontab(hour=2, minute=0),  # Daily at 02:00 UTC
    },
    "send-deadline-reminders-daily": {
        "task": "app.tasks.deadline_tasks.send_deadline_reminders",
        "schedule": crontab(hour=8, minute=0),  # Daily at 08:00 UTC
    },
}
