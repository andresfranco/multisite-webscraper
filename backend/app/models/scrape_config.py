"""ScrapeConfig model - replaces hardcoded scraper classes."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ScrapeConfig(Base):
    """Configuration for scraping a specific website."""

    __tablename__ = "scrape_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    base_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Page fetching
    use_headless_browser: Mapped[bool] = mapped_column(Boolean, default=False)
    wait_for_selector: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    custom_headers: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Pagination
    pagination_type: Mapped[str] = mapped_column(String(20), default="none")
    pagination_selector: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    max_pages: Mapped[int] = mapped_column(Integer, default=1)

    # Item extraction
    item_selector: Mapped[str] = mapped_column(String(500), nullable=False)
    fields: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Rate limiting
    request_delay_ms: Mapped[int] = mapped_column(Integer, default=1000)
    concurrent_requests: Mapped[int] = mapped_column(Integer, default=1)

    # Scheduling
    schedule_cron: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    jobs: Mapped[list["ScrapeJob"]] = relationship(
        back_populates="config", cascade="all, delete-orphan"
    )
    schedules: Mapped[list["ScrapeSchedule"]] = relationship(  # type: ignore[name-defined]
        back_populates="config", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<ScrapeConfig(id={self.id}, name='{self.name}', domain='{self.domain}')>"
        )
