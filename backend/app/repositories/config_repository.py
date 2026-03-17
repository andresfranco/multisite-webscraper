"""Repository for ScrapeConfig CRUD operations."""
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scrape_config import ScrapeConfig
from app.repositories.base_repository import BaseRepository


class ConfigRepository(BaseRepository[ScrapeConfig]):
    """Async repository for ScrapeConfig model."""

    def __init__(self, session: AsyncSession):
        super().__init__(ScrapeConfig, session)

    async def get_by_domain(self, domain: str) -> Sequence[ScrapeConfig]:
        """Get all configs for a specific domain."""
        stmt = select(ScrapeConfig).where(ScrapeConfig.domain == domain)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_active(self) -> Sequence[ScrapeConfig]:
        """Get all active configs."""
        stmt = select(ScrapeConfig).where(ScrapeConfig.is_active.is_(True))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_scheduled(self) -> Sequence[ScrapeConfig]:
        """Get all configs with a schedule."""
        stmt = select(ScrapeConfig).where(
            ScrapeConfig.schedule_cron.isnot(None),
            ScrapeConfig.is_active.is_(True),
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
