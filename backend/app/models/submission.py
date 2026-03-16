"""Submission and SubmissionDeadline ORM models."""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # PSUR | DSUR | RMP
    cycle: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. PSUR-12
    data_lock_point: Mapped[date] = mapped_column(Date, nullable=False)
    submission_due: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="Planned"
    )  # Planned | In-Progress | Submitted | Overdue
    authority: Mapped[str] = mapped_column(String(50), nullable=False, default="EMA")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    product = relationship("Product", back_populates="submissions")
    deadlines = relationship("SubmissionDeadline", back_populates="submission", lazy="selectin")
    qc_checks = relationship("QCCheck", back_populates="submission", lazy="selectin")
    capas = relationship("CAPA", back_populates="submission", lazy="selectin")


class SubmissionDeadline(Base):
    __tablename__ = "submission_deadlines"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False, index=True
    )
    milestone: Mapped[str] = mapped_column(String(50), nullable=False)  # DLP | Draft | QC | Filing
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    submission = relationship("Submission", back_populates="deadlines")
