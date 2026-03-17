"""Base async repository with common CRUD operations."""
from typing import Any, Generic, Optional, Sequence, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Generic async repository for SQLAlchemy models."""

    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, record_id: int) -> Optional[T]:
        """Get a single record by primary key."""
        return await self.session.get(self.model, record_id)

    async def get_all(self, offset: int = 0, limit: int = 100) -> Sequence[T]:
        """Get all records with pagination."""
        stmt = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count(self) -> int:
        """Get total count of records."""
        stmt = select(func.count()).select_from(self.model)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def create(self, obj: T) -> T:
        """Create a new record."""
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj: T, data: dict[str, Any]) -> T:
        """Update a record with the given data dict."""
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj: T) -> None:
        """Delete a record."""
        await self.session.delete(obj)
        await self.session.flush()

    async def delete_by_id(self, record_id: int) -> bool:
        """Delete a record by ID. Returns True if deleted."""
        obj = await self.get_by_id(record_id)
        if obj is None:
            return False
        await self.delete(obj)
        return True
