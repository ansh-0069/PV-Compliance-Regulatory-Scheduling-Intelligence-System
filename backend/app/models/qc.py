"""QC Check and QC Finding ORM models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class QCCheck(Base):
    __tablename__ = "qc_checks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False, index=True
    )
    file_key: Mapped[str] = mapped_column(String(500), nullable=False)  # MinIO object key
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="Pending"
    )  # Pending | Running | Passed | Failed
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    submission = relationship("Submission", back_populates="qc_checks")
    findings = relationship("QCFinding", back_populates="qc_check", lazy="selectin")


class QCFinding(Base):
    __tablename__ = "qc_findings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    qc_check_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("qc_checks.id"), nullable=False, index=True
    )
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # Critical | Major | Minor | Info
    section: Mapped[str] = mapped_column(String(100), nullable=True)  # e.g. Section 3.2
    description: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    qc_check = relationship("QCCheck", back_populates="findings")
