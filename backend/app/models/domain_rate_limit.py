"""Domain-level scrape rate limiting settings."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Integer, String, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DomainRateLimit(Base):
    """Stores per-domain request pacing information."""

    __tablename__ = "domain_rate_limits"

    id: Mapped[int] = mapped_column(primary_key=True)
    domain: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    delay_ms: Mapped[int] = mapped_column(Integer, default=1000)
    last_request: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
