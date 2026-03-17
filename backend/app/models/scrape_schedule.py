"""ScrapeSchedule model — Celery Beat entries managed via the API."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ScrapeSchedule(Base):
    """Periodic schedule that auto-triggers a scrape job via Celery Beat."""

    __tablename__ = "scrape_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # FK to the config that will be scraped
    config_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("scrape_configs.id", ondelete="CASCADE"), nullable=False
    )

    # Cron expression, e.g. "0 6 * * *" = every day at 06:00 UTC
    cron_expression: Mapped[str] = mapped_column(String(100), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Audit
    last_run_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    next_run_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationship
    config: Mapped["ScrapeConfig"] = relationship(back_populates="schedules")  # type: ignore[name-defined]

    def __repr__(self) -> str:
        return (
            f"<ScrapeSchedule(id={self.id}, name='{self.name}', "
            f"cron='{self.cron_expression}')>"
        )
