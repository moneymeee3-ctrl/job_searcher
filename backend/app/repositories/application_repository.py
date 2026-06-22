"""EMBEDHUNT AI — Application Repository"""
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.application import Application, ApplicationStatus, ApplicationOutcome
from app.common.base_repository import BaseRepository

class ApplicationRepository(BaseRepository[Application]):
    def __init__(self, db: AsyncSession): super().__init__(db, Application)

    async def get_by_user(self, user_id: str) -> list[Application]:
        r = await self.db.execute(select(Application).where(Application.user_id == user_id).order_by(Application.created_at.desc()))
        return list(r.scalars().all())

    async def update_status(self, app_id: str, status: ApplicationStatus, **extra):
        await self.db.execute(update(Application).where(Application.id == app_id).values(status=status, **extra))

    async def update_outcome(self, app_id: str, outcome: ApplicationOutcome):
        from datetime import datetime, timezone
        await self.db.execute(update(Application).where(Application.id == app_id).values(outcome=outcome, responded_at=datetime.now(timezone.utc).isoformat()))
