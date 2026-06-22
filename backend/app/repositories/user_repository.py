"""EMBEDHUNT AI — User Repository"""
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.common.base_repository import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession): super().__init__(db, User)

    async def get_by_email(self, email: str) -> Optional[User]:
        r = await self.db.execute(select(User).where(User.email == email.lower())); return r.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        r = await self.db.execute(select(User).where(User.username == username.lower())); return r.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        r = await self.db.execute(select(User.id).where(User.email == email.lower())); return r.scalar_one_or_none() is not None

    async def username_exists(self, username: str) -> bool:
        r = await self.db.execute(select(User.id).where(User.username == username.lower())); return r.scalar_one_or_none() is not None

    async def update_last_login(self, user_id: str):
        from datetime import datetime, timezone
        await self.db.execute(update(User).where(User.id == user_id).values(last_login_at=datetime.now(timezone.utc).isoformat(), failed_login_attempts=0, locked_until=None))

    async def increment_failed_login(self, user_id: str) -> int:
        r = await self.db.execute(select(User.failed_login_attempts).where(User.id == user_id))
        count = (r.scalar_one_or_none() or 0) + 1
        await self.db.execute(update(User).where(User.id == user_id).values(failed_login_attempts=count)); return count

    async def set_locked_until(self, user_id: str, until: str):
        await self.db.execute(update(User).where(User.id == user_id).values(locked_until=until))

    async def verify_email(self, user_id: str):
        await self.db.execute(update(User).where(User.id == user_id).values(is_verified=True, email_verify_token=None))

    async def set_verify_token(self, user_id: str, token: str):
        await self.db.execute(update(User).where(User.id == user_id).values(email_verify_token=token))

    async def set_reset_token(self, user_id: str, token: str):
        await self.db.execute(update(User).where(User.id == user_id).values(password_reset_token=token))

    async def update_password(self, user_id: str, hash: str):
        await self.db.execute(update(User).where(User.id == user_id).values(password_hash=hash, password_reset_token=None))
