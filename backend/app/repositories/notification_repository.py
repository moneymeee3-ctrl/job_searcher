"""EMBEDHUNT AI — Notification Repository"""
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.base_repository import BaseRepository
from app.models.notification import Notification


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Notification)

    async def get_by_user(
        self, user_id: str, *, unread_only: bool = False, limit: int = 50
    ) -> list[Notification]:
        stmt = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            stmt = stmt.where(Notification.is_read.is_(False))
        stmt = stmt.order_by(Notification.created_at.desc()).limit(limit)
        r = await self.db.execute(stmt)
        return list(r.scalars().all())

    async def unread_count(self, user_id: str) -> int:
        r = await self.db.execute(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
        )
        return int(r.scalar_one())

    async def mark_read(self, user_id: str, notification_id: str) -> bool:
        r = await self.db.execute(
            update(Notification)
            .where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
            .values(is_read=True)
        )
        return r.rowcount > 0

    async def mark_all_read(self, user_id: str) -> int:
        r = await self.db.execute(
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
            .values(is_read=True)
        )
        return r.rowcount
