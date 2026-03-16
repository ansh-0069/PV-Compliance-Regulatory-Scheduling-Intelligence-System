"""Product ORM model."""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    active_substance: Mapped[str] = mapped_column(String(255), nullable=False)
    mah: Mapped[str] = mapped_column(String(255), nullable=False)  # Marketing Authorization Holder
    ibd: Mapped[date] = mapped_column(Date, nullable=False)  # International Birth Date
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    submissions = relationship("Submission", back_populates="product", lazy="selectin")
    audit_scores = relationship("AuditScore", back_populates="product", lazy="selectin")
