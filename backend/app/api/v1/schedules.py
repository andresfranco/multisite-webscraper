"""Schedules API router — CRUD for ScrapeSchedule (Celery Beat entries)."""
from __future__ import annotations

from typing import List

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.scrape_config import ScrapeConfig
from app.models.scrape_schedule import ScrapeSchedule
from app.schemas.schedule import (
    ScheduleCreateRequest,
    ScheduleResponse,
    ScheduleUpdateRequest,
)

logger = structlog.get_logger()

router = APIRouter()


@router.get("", response_model=List[ScheduleResponse])
async def list_schedules(
    session: AsyncSession = Depends(get_session),
) -> List[ScheduleResponse]:
    """List all schedules."""
    stmt = select(ScrapeSchedule).order_by(ScrapeSchedule.id)
    result = await session.execute(stmt)
    schedules = result.scalars().all()
    return [ScheduleResponse.model_validate(s) for s in schedules]


@router.post("", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    body: ScheduleCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> ScheduleResponse:
    """Create a new schedule for an existing config."""
    # Verify config exists
    config = await session.get(ScrapeConfig, body.config_id)
    if config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ScrapeConfig {body.config_id} not found",
        )

    schedule = ScrapeSchedule(
        name=body.name,
        config_id=body.config_id,
        cron_expression=body.cron_expression,
        is_active=body.is_active,
    )
    session.add(schedule)
    await session.commit()
    await session.refresh(schedule)

    logger.info("schedule_created", schedule_id=schedule.id, config_id=body.config_id)
    return ScheduleResponse.model_validate(schedule)


@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: int,
    session: AsyncSession = Depends(get_session),
) -> ScheduleResponse:
    """Get a single schedule by ID."""
    schedule = await session.get(ScrapeSchedule, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    return ScheduleResponse.model_validate(schedule)


@router.patch("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    body: ScheduleUpdateRequest,
    session: AsyncSession = Depends(get_session),
) -> ScheduleResponse:
    """Update a schedule (partial)."""
    schedule = await session.get(ScrapeSchedule, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")

    update_data = body.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(schedule, key, value)

    await session.commit()
    await session.refresh(schedule)
    logger.info("schedule_updated", schedule_id=schedule_id)
    return ScheduleResponse.model_validate(schedule)


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_schedule(
    schedule_id: int,
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete a schedule."""
    schedule = await session.get(ScrapeSchedule, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    await session.delete(schedule)
    await session.commit()
    logger.info("schedule_deleted", schedule_id=schedule_id)


@router.post("/{schedule_id}/trigger", response_model=dict)
async def trigger_schedule(
    schedule_id: int,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Manually trigger a schedule's config to run immediately."""
    from datetime import datetime, timezone

    from app.core.tasks.scrape_task import execute_scrape_job
    from app.models.scrape_job import ScrapeJob

    schedule = await session.get(ScrapeSchedule, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")

    # Create a new job
    job = ScrapeJob(config_id=schedule.config_id, status="pending")
    session.add(job)
    await session.commit()
    await session.refresh(job)

    # Dispatch the Celery task
    execute_scrape_job.delay(job.id, schedule.config_id)

    # Update schedule last_run_at
    schedule.last_run_at = datetime.now(timezone.utc)
    await session.commit()

    logger.info("schedule_triggered_manually", schedule_id=schedule_id, job_id=job.id)
    return {"job_id": job.id, "message": "Scrape job dispatched"}
