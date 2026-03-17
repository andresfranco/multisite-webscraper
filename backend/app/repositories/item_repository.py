"""Repository for ScrapedItem CRUD operations."""
from typing import Optional, Sequence

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scraped_item import ScrapedItem
from app.repositories.base_repository import BaseRepository


class ItemRepository(BaseRepository[ScrapedItem]):
    """Async repository for ScrapedItem model."""

    def __init__(self, session: AsyncSession):
        super().__init__(ScrapedItem, session)

    async def get_by_job(
        self, job_id: int, offset: int = 0, limit: int = 100
    ) -> Sequence[ScrapedItem]:
        """Get all items for a specific job."""
        stmt = (
            select(ScrapedItem)
            .where(ScrapedItem.job_id == job_id)
            .order_by(desc(ScrapedItem.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_config(
        self, config_id: int, offset: int = 0, limit: int = 100
    ) -> Sequence[ScrapedItem]:
        """Get all items for a specific config."""
        stmt = (
            select(ScrapedItem)
            .where(ScrapedItem.config_id == config_id)
            .order_by(desc(ScrapedItem.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_content_hash(self, content_hash: str) -> Optional[ScrapedItem]:
        """Check if an item with this content hash already exists."""
        stmt = select(ScrapedItem).where(ScrapedItem.content_hash == content_hash)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_by_job(self, job_id: int) -> int:
        """Count items for a specific job."""
        stmt = (
            select(func.count())
            .select_from(ScrapedItem)
            .where(ScrapedItem.job_id == job_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def count_by_config(self, config_id: int) -> int:
        """Count items for a specific config."""
        stmt = (
            select(func.count())
            .select_from(ScrapedItem)
            .where(ScrapedItem.config_id == config_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def create_if_new(self, item: ScrapedItem) -> tuple[ScrapedItem, bool]:
        """Create item if content_hash does not already exist."""
        if item.content_hash:
            existing = await self.get_by_content_hash(item.content_hash)
            if existing:
                return existing, False
        created = await self.create(item)
        return created, True
