"""Repository for ScrapeJob CRUD operations."""
from typing import Optional, Sequence

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.scrape_job import ScrapeJob
from app.repositories.base_repository import BaseRepository


class JobRepository(BaseRepository[ScrapeJob]):
    """Async repository for ScrapeJob model."""

    def __init__(self, session: AsyncSession):
        super().__init__(ScrapeJob, session)

    async def get_by_config(
        self, config_id: int, offset: int = 0, limit: int = 50
    ) -> Sequence[ScrapeJob]:
        """Get all jobs for a specific config."""
        stmt = (
            select(ScrapeJob)
            .where(ScrapeJob.config_id == config_id)
            .order_by(desc(ScrapeJob.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_status(self, status: str) -> Sequence[ScrapeJob]:
        """Get all jobs with a specific status."""
        stmt = (
            select(ScrapeJob)
            .where(ScrapeJob.status == status)
            .order_by(desc(ScrapeJob.created_at))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_recent(self, limit: int = 10) -> Sequence[ScrapeJob]:
        """Get the most recent jobs."""
        stmt = select(ScrapeJob).order_by(desc(ScrapeJob.created_at)).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_with_items(self, job_id: int) -> Optional[ScrapeJob]:
        """Get a job with its scraped items eagerly loaded."""
        stmt = (
            select(ScrapeJob)
            .options(selectinload(ScrapeJob.items))
            .where(ScrapeJob.id == job_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(
        self, job_id: int, status: str, **kwargs
    ) -> Optional[ScrapeJob]:
        """Update job status and optional fields."""
        job = await self.get_by_id(job_id)
        if job is None:
            return None
        job.status = status
        for key, value in kwargs.items():
            if hasattr(job, key):
                setattr(job, key, value)
        await self.session.flush()
        await self.session.refresh(job)
        return job
