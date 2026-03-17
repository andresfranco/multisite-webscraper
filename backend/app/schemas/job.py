"""Pydantic schemas for ScrapeJob API endpoints."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    """Schema for starting a new scrape job."""

    config_id: int = Field(..., description="ID of the ScrapeConfig to run")


class JobResponse(BaseModel):
    """Schema for ScrapeJob API responses."""

    id: int
    config_id: Optional[int]
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    pages_scraped: int
    items_found: int
    items_created: int
    items_skipped: int
    errors: int
    error_message: Optional[str]
    celery_task_id: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class JobProgress(BaseModel):
    """Schema for real-time job progress (WebSocket)."""

    job_id: int
    status: str
    pages_scraped: int
    pages_total: int
    items_found: int
    items_created: int
    items_skipped: int
    errors: int
    current_url: Optional[str] = None
    elapsed_seconds: float = 0
    estimated_remaining_seconds: Optional[float] = None
