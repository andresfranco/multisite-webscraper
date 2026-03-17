"""Pydantic schemas for scrape schedules."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ScheduleCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    config_id: int
    cron_expression: str = Field(
        min_length=9,
        max_length=100,
        description="Standard 5-field cron expression, e.g. '0 6 * * *'",
    )
    is_active: bool = True


class ScheduleUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    cron_expression: Optional[str] = Field(default=None, min_length=9, max_length=100)
    is_active: Optional[bool] = None


class ScheduleResponse(BaseModel):
    id: int
    name: str
    config_id: int
    cron_expression: str
    is_active: bool
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
