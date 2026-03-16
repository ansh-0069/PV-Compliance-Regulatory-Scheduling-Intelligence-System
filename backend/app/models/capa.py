"""CAPA, CAPAAction, CAPAHistory, and RootCauseCategory ORM models."""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RootCauseCategory(Base):
    __tablename__ = "root_cause_categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)  # e.g. RC-001
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g. Process Deviation

    # Relationships
    capas = relationship("CAPA", back_populates="root_cause_category")


class CAPA(Base):
    __tablename__ = "capas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="Open"
    )  # Open | Investigation | Corrective Action | Verification | Closed
    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Medium"
    )  # Critical | High | Medium | Low
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    target_closure: Mapped[date | None] = mapped_column(Date, nullable=True)
    root_cause_category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("root_cause_categories.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    submission = relationship("Submission", back_populates="capas")
    root_cause_category = relationship("RootCauseCategory", back_populates="capas")
    actions = relationship("CAPAAction", back_populates="capa", lazy="selectin")
    history = relationship("CAPAHistory", back_populates="capa", lazy="selectin", order_by="CAPAHistory.changed_at")


class CAPAAction(Base):
    __tablename__ = "capa_actions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    capa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("capas.id"), nullable=False, index=True
    )
    action_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # Corrective | Preventive
    description: Mapped[str] = mapped_column(Text, nullable=False)
    assignee: Mapped[str] = mapped_column(String(255), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Pending"
    )  # Pending | In-Progress | Complete
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    capa = relationship("CAPA", back_populates="actions")


class CAPAHistory(Base):
    __tablename__ = "capa_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    capa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("capas.id"), nullable=False, index=True
    )
    from_status: Mapped[str] = mapped_column(String(30), nullable=False)
    to_status: Mapped[str] = mapped_column(String(30), nullable=False)
    changed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    capa = relationship("CAPA", back_populates="history")
