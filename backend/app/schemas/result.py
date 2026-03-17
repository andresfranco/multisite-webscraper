"""Pydantic schemas for ScrapedItem (results) API endpoints."""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ScrapedItemResponse(BaseModel):
    """Schema for ScrapedItem API responses."""

    id: int
    job_id: int
    config_id: Optional[int]
    source_url: str
    item_url: Optional[str]
    data: dict[str, Any]
    content_hash: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ResultsListResponse(BaseModel):
    """Paginated response for listing scraped items."""

    items: list[ScrapedItemResponse]
    total: int
    page: int
    page_size: int
    pages: int


class ResultStats(BaseModel):
    """Aggregated statistics for scraped results."""

    total_items: int = 0
    total_jobs: int = 0
    total_configs: int = 0
    items_by_domain: dict[str, int] = Field(default_factory=dict)
    jobs_by_status: dict[str, int] = Field(default_factory=dict)
