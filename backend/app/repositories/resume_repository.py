"""EMBEDHUNT AI — Resume Repository"""
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.resume import Resume, ResumeStatus
from app.common.base_repository import BaseRepository

class ResumeRepository(BaseRepository[Resume]):
    def __init__(self, db: AsyncSession): super().__init__(db, Resume)

    async def get_by_user(self, user_id: str) -> list[Resume]:
        r = await self.db.execute(select(Resume).where(Resume.user_id == user_id).order_by(Resume.is_primary.desc(), Resume.created_at.desc()))
        return list(r.scalars().all())

    async def get_primary(self, user_id: str) -> Optional[Resume]:
        r = await self.db.execute(select(Resume).where(Resume.user_id == user_id, Resume.is_primary == True, Resume.status == ResumeStatus.PARSED))
        resume = r.scalar_one_or_none()
        if not resume:
            r2 = await self.db.execute(select(Resume).where(Resume.user_id == user_id, Resume.status == ResumeStatus.PARSED).limit(1))
            resume = r2.scalar_one_or_none()
        return resume

    async def get_for_user(self, resume_id: str, user_id: str) -> Optional[Resume]:
        r = await self.db.execute(select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)); return r.scalar_one_or_none()

    async def clear_primary(self, user_id: str):
        await self.db.execute(update(Resume).where(Resume.user_id == user_id, Resume.is_primary == True).values(is_primary=False))

    async def set_status(self, resume_id: str, status: ResumeStatus):
        await self.db.execute(update(Resume).where(Resume.id == resume_id).values(status=status))

    async def save_parsed(self, resume_id: str, **fields):
        await self.db.execute(update(Resume).where(Resume.id == resume_id).values(**fields, status=ResumeStatus.PARSED))
