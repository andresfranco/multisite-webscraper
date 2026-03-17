"""Scrape job management endpoints."""
from datetime import datetime, timezone
from typing import Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

log = structlog.get_logger(__name__)

from app.database import get_session
from app.models.scrape_job import ScrapeJob
from app.repositories.config_repository import ConfigRepository
from app.repositories.job_repository import JobRepository
from app.schemas.job import JobCreate, JobResponse

router = APIRouter()


@router.get("/", response_model=list[JobResponse])
async def list_jobs(
    status: Optional[str] = Query(None, description="Filter by status"),
    config_id: Optional[int] = Query(None, description="Filter by config ID"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
):
    """List scrape jobs with optional filtering."""
    repo = JobRepository(session)

    if status:
        jobs = await repo.get_by_status(status)
    elif config_id:
        jobs = await repo.get_by_config(config_id, offset=offset, limit=limit)
    else:
        jobs = await repo.get_all(offset=offset, limit=limit)

    return jobs


@router.post("/", response_model=JobResponse, status_code=201)
async def create_job(
    job_in: JobCreate,
    session: AsyncSession = Depends(get_session),
):
    """Start a new scrape job for the given config."""
    # Verify config exists
    config_repo = ConfigRepository(session)
    config = await config_repo.get_by_id(job_in.config_id)
    if config is None:
        raise HTTPException(status_code=404, detail="Config not found")

    # Create the job record and commit BEFORE dispatching to Celery.
    # The worker runs in a separate process with its own DB connection, so it
    # will only see the job once the transaction is committed here.
    job_repo = JobRepository(session)
    db_job = ScrapeJob(
        config_id=job_in.config_id,
        status="pending",
    )
    created_job = await job_repo.create(db_job)
    await session.commit()
    await session.refresh(created_job)

    # Dispatch Celery task now that the job row is visible to other connections
    try:
        from app.core.tasks.scrape_task import execute_scrape_job

        task = execute_scrape_job.delay(created_job.id, job_in.config_id)
        created_job.celery_task_id = task.id
        await session.commit()
        await session.refresh(created_job)
    except Exception:
        # If Celery is unavailable, job stays in pending state
        pass

    return created_job


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get a single scrape job by ID."""
    repo = JobRepository(session)
    job = await repo.get_by_id(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/cancel")
async def cancel_job(
    job_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Cancel a running scrape job."""
    repo = JobRepository(session)
    job = await repo.get_by_id(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status not in ("pending", "running"):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job with status '{job.status}'",
        )

    # Revoke Celery task if available
    if job.celery_task_id:
        try:
            from celery_app import celery

            celery.control.revoke(job.celery_task_id, terminate=True)
        except Exception:
            pass

    await repo.update_status(
        job_id, "cancelled", completed_at=datetime.now(timezone.utc)
    )
    return {"message": "Job cancelled"}
