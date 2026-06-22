"""EMBEDHUNT AI — Notifications API"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.auth.permissions import get_current_user_id
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", summary="Get user notifications")
async def get_notifications(
    unread_only: bool = False,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await NotificationService(db).get_notifications(user_id, unread_only=unread_only)


@router.post("/{notification_id}/read", summary="Mark a notification as read")
async def mark_read(
    notification_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await NotificationService(db).mark_read(user_id, notification_id)


@router.post("/read-all", summary="Mark all notifications as read")
async def mark_all_read(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await NotificationService(db).mark_all_read(user_id)
