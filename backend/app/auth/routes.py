"""EMBEDHUNT AI — Auth Routes (mounted at /api/v1/auth)"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.auth.service import AuthService
from app.auth.permissions import get_current_user_id
from app.schemas.auth import (RegisterRequest, LoginRequest, RefreshRequest,
    ForgotPasswordRequest, ResetPasswordRequest, VerifyEmailRequest,
    TokenResponse, UserResponse, MessageResponse)
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService(db).register(req.email, req.username, req.password, req.first_name, req.last_name, req.role)

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    ip = request.client.host if request.client else "unknown"
    return await AuthService(db).login(req.email, req.password, ip)

@router.post("/refresh", response_model=TokenResponse)
async def refresh(req: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService(db).refresh(req.refresh_token)

@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(req: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    msg = await AuthService(db).verify_email(req.token); return {"message": msg}

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(req: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    await AuthService(db).forgot_password(req.email)
    return {"message": "If account exists, reset link sent."}

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(req: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    await AuthService(db).reset_password(req.token, req.new_password)
    return {"message": "Password reset successful."}

@router.get("/me", response_model=UserResponse)
async def me(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    from fastapi import HTTPException
    user = await UserRepository(db).get_by_id(user_id)
    if not user: raise HTTPException(404, "User not found")
    return user
