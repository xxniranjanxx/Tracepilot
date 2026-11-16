
from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class IncidentRecord(Base):
    __tablename__ = "incident_records"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    incident_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    short_description: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    resolution_notes: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    resolution_category: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    resolution_time_hours: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    sla_breached: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True
    )
