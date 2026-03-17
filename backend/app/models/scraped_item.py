"""ScrapedItem model - stores extracted data from scraping."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ScrapedItem(Base):
    """A single item extracted during a scrape job."""

    __tablename__ = "scraped_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("scrape_jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    config_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("scrape_configs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    item_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    data: Mapped[dict] = mapped_column(JSON, nullable=False)
    content_hash: Mapped[Optional[str]] = mapped_column(
        String(64), unique=True, nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    job: Mapped["ScrapeJob"] = relationship(back_populates="items")

    def __repr__(self) -> str:
        return (
            f"<ScrapedItem(id={self.id}, job_id={self.job_id}, "
            f"source_url='{self.source_url[:50]}')>"
        )
