"""EMBEDHUNT AI — Auth Service"""
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.jwt import (create_access_token, create_refresh_token,
    create_email_verify_token, create_password_reset_token, decode_token, TokenType)
from app.auth.password import hash_password, verify_password
from app.auth.permissions import UserRole
from app.repositories.user_repository import UserRepository
from app.config.logging import get_logger
from app.common.constants import MAX_FAILED_LOGIN_ATTEMPTS, LOCKOUT_DURATION_MINUTES
from app.config.settings import settings
logger = get_logger(__name__)

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db; self.repo = UserRepository(db)

    async def register(self, email: str, username: str, password: str, first_name: str, last_name: str, role: UserRole = UserRole.CANDIDATE) -> dict:
        if await self.repo.email_exists(email): raise HTTPException(409, "Email already registered")
        if await self.repo.username_exists(username): raise HTTPException(409, "Username taken")
        user = await self.repo.create(
            email=email.lower(), username=username.lower(), password_hash=hash_password(password),
            first_name=first_name.strip(), last_name=last_name.strip(), role=role)
        token = create_email_verify_token(user.email)
        await self.repo.set_verify_token(user.id, token)
        logger.info("user_registered", user_id=user.id, role=role.value)
        return self._tokens(user)

    async def login(self, email: str, password: str, ip: str = "unknown") -> dict:
        user = await self.repo.get_by_email(email.lower())
        err = HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
        if not user: raise err
        if not user.is_active: raise HTTPException(403, "Account deactivated")
        if user.locked_until:
            locked = datetime.fromisoformat(user.locked_until)
            if datetime.now(timezone.utc) < locked:
                mins = int((locked - datetime.now(timezone.utc)).total_seconds()/60)+1
                raise HTTPException(429, f"Account locked. Try again in {mins} minutes.")
        if not verify_password(password, user.password_hash):
            count = await self.repo.increment_failed_login(user.id)
            if count >= MAX_FAILED_LOGIN_ATTEMPTS:
                until = (datetime.now(timezone.utc)+timedelta(minutes=LOCKOUT_DURATION_MINUTES)).isoformat()
                await self.repo.set_locked_until(user.id, until)
            raise err
        await self.repo.update_last_login(user.id)
        logger.info("user_login", user_id=user.id, ip=ip)
        return self._tokens(user)

    async def refresh(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token, TokenType.REFRESH)
        user = await self.repo.get_by_id(payload["sub"])
        if not user or not user.is_active: raise HTTPException(401, "User not found")
        return {"access_token": create_access_token(user.id, user.role.value),
                "refresh_token": create_refresh_token(user.id),
                "token_type": "bearer", "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES*60}

    async def verify_email(self, token: str) -> str:
        payload = decode_token(token, TokenType.EMAIL_VERIFY)
        user = await self.repo.get_by_email(payload["sub"])
        if not user: raise HTTPException(404, "User not found")
        if user.is_verified: return "Already verified"
        await self.repo.verify_email(user.id); return "Email verified"

    async def forgot_password(self, email: str) -> None:
        user = await self.repo.get_by_email(email.lower())
        if user:
            t = create_password_reset_token(user.email)
            await self.repo.set_reset_token(user.id, t)
            logger.info("password_reset_requested", user_id=user.id)

    async def reset_password(self, token: str, new_password: str) -> None:
        payload = decode_token(token, TokenType.PASSWORD_RESET)
        user = await self.repo.get_by_email(payload["sub"])
        if not user: raise HTTPException(404, "User not found")
        await self.repo.update_password(user.id, hash_password(new_password))

    def _tokens(self, user) -> dict:
        return {"access_token": create_access_token(user.id, user.role.value),
                "refresh_token": create_refresh_token(user.id),
                "token_type": "bearer", "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES*60,
                "user_id": user.id, "role": user.role.value}
