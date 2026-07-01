"""EMBEDHUNT AI — Career Twin Repository."""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.career_twin import CareerTwin
from app.common.base_repository import BaseRepository


class CareerTwinRepository(BaseRepository[CareerTwin]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, CareerTwin)

    async def get_by_user(self, user_id: str) -> Optional[CareerTwin]:
        r = await self.db.execute(select(CareerTwin).where(CareerTwin.user_id == user_id))
        return r.scalar_one_or_none()
