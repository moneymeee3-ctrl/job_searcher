"""EMBEDHUNT AI — Generic Async Repository Base"""
from typing import Generic, Optional, Type, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.base import BaseModel

T = TypeVar("T", bound=BaseModel)

class BaseRepository(Generic[T]):
    def __init__(self, db: AsyncSession, model: Type[T]):
        self.db = db; self.model = model

    async def get_by_id(self, id: str) -> Optional[T]:
        r = await self.db.execute(select(self.model).where(self.model.id == id))
        return r.scalar_one_or_none()

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[T]:
        r = await self.db.execute(select(self.model).limit(limit).offset(offset))
        return list(r.scalars().all())

    async def create(self, **kwargs) -> T:
        obj = self.model(**kwargs); self.db.add(obj)
        await self.db.flush(); await self.db.refresh(obj); return obj

    async def delete(self, obj: T) -> None:
        await self.db.delete(obj)
