"""EMBEDHUNT AI — Auth Service"""
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.jwt import create_access_token, create_refresh_token, create_email_verify_token, create_password_reset_token, decode_token, TokenType
from app.auth.password import hash_password, verify_password
from app.auth.permissions import UserRole
from app.repositories.user_repository import UserRepository
from app.config.logging import get_logger
from app.common.constants import MAX_FAILED_LOGIN_ATTEMPTS, LOCKOUT_DURATION_MINUTES

logger = get_logger(__name__)

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)

    async def register(self, email: str, username: str, password: str, first_name: str, last_name: str, role: UserRole = UserRole.CANDIDATE) -> dict:
        if await self.repo.email_exists(email.lower()):
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
        if await self.repo.username_exists(username.lower()):
            raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken")
        user = await self.repo.create(
            email=email.lower(), username=username.lower(),
            password_hash=hash_password(password),
            first_name=first_name.strip(), last_name=last_name.strip(),
            role=role, is_active=True, is_verified=False
        )
        token = create_email_verify_token(user.email)
        await self.repo.set_verify_token(user.id, token)
        logger.info("user_registered", user_id=user.id, role=role.value)
        return self._tokens_and_user(user, "Registration successful")

    async def login(self, email: str, password: str, ip: str = "unknown") -> dict:
        user = await self.repo.get_by_email(email.lower())
        _err = HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
        if not user: raise _err
        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Account deactivated")
        if user.locked_until:
            locked = datetime.fromisoformat(user.locked_until)
            if datetime.now(timezone.utc) < locked:
                mins = int((locked - datetime.now(timezone.utc)).total_seconds() / 60) + 1
                raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, f"Account locked. Try in {mins} min.")
        if not verify_password(password, user.password_hash):
            n = await self.repo.increment_failed_login(user.id)
            if n >= MAX_FAILED_LOGIN_ATTEMPTS:
                until = (datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_DURATION_MINUTES)).isoformat()
                await self.repo.set_locked_until(user.id, until)
                raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, f"Too many failures. Locked {LOCKOUT_DURATION_MINUTES} min.")
            raise _err
        await self.repo.update_last_login(user.id)
        logger.info("user_login", user_id=user.id, ip=ip)
        return self._tokens_and_user(user, "Login successful")

    async def refresh(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token, TokenType.REFRESH)
        user = await self.repo.get_by_id(payload["sub"])
        if not user or not user.is_active:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
        from app.config.settings import settings
        return {"access_token": create_access_token(user.id, user.role.value),
                "refresh_token": create_refresh_token(user.id),
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60}

    async def verify_email(self, token: str) -> str:
        payload = decode_token(token, TokenType.EMAIL_VERIFY)
        user = await self.repo.get_by_email(payload["sub"])
        if not user: raise HTTPException(404, "User not found")
        if user.is_verified: return "Already verified"
        await self.repo.verify_email(user.id)
        return "Email verified successfully"

    async def forgot_password(self, email: str) -> str:
        user = await self.repo.get_by_email(email.lower())
        if user:
            token = create_password_reset_token(user.email)
            await self.repo.set_reset_token(user.id, token)
        return "If that email exists, a reset link was sent"

    async def reset_password(self, token: str, new_password: str) -> str:
        payload = decode_token(token, TokenType.PASSWORD_RESET)
        user = await self.repo.get_by_email(payload["sub"])
        if not user: raise HTTPException(404, "User not found")
        await self.repo.update_password(user.id, hash_password(new_password))
        return "Password reset successfully"

    def _tokens_and_user(self, user, message: str) -> dict:
        from app.config.settings import settings
        return {
            "access_token": create_access_token(user.id, user.role.value),
            "refresh_token": create_refresh_token(user.id),
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id, "email": user.email, "username": user.username,
                "first_name": user.first_name, "last_name": user.last_name,
                "full_name": user.full_name, "role": user.role.value,
                "is_verified": user.is_verified, "is_premium": user.is_premium,
            },
            "message": message
        }
