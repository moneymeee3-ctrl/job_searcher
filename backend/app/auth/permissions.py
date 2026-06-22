"""EMBEDHUNT AI — RBAC Permissions"""
from enum import Enum
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.jwt import decode_token, TokenType

class UserRole(str, Enum):
    CANDIDATE = "candidate"; RECRUITER = "recruiter"
    COMPANY_ADMIN = "company_admin"; PLATFORM_ADMIN = "platform_admin"

ROLE_HIERARCHY = {UserRole.PLATFORM_ADMIN: 4, UserRole.COMPANY_ADMIN: 3, UserRole.RECRUITER: 2, UserRole.CANDIDATE: 1}

bearer = HTTPBearer(auto_error=True)

async def get_token_payload(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    return decode_token(creds.credentials, TokenType.ACCESS)

async def get_current_user_id(payload: dict = Depends(get_token_payload)) -> str: return payload["sub"]
async def get_current_user_role(payload: dict = Depends(get_token_payload)) -> UserRole: return UserRole(payload.get("role", "candidate"))

def require_role(*roles: UserRole):
    async def _check(role: UserRole = Depends(get_current_user_role)):
        if role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"Required: {[r.value for r in roles]}")
        return role
    return _check

def require_min_role(min_role: UserRole):
    async def _check(role: UserRole = Depends(get_current_user_role)):
        if ROLE_HIERARCHY.get(role, 0) < ROLE_HIERARCHY.get(min_role, 0):
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"Minimum role required: {min_role.value}")
        return role
    return _check
