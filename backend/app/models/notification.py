"""EMBEDHUNT AI — Notification Model"""
from typing import Optional
from sqlalchemy import String, Boolean, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum
from app.database.base import BaseModel

class NotificationType(str, Enum):
    NEW_JOB_MATCH="new_job_match"; APPLICATION_UPDATE="application_update"
    PROFILE_TIP="profile_tip"; INTERVIEW_REMINDER="interview_reminder"
    WEEKLY_SUMMARY="weekly_summary"; SYSTEM="system"

class NotificationChannel(str, Enum):
    IN_APP="in_app"; EMAIL="email"; PUSH="push"

class Notification(BaseModel):
    __tablename__ = "notifications"
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    type: Mapped[NotificationType] = mapped_column(SAEnum(NotificationType, name="notif_type_enum"), nullable=False)
    channel: Mapped[NotificationChannel] = mapped_column(SAEnum(NotificationChannel, name="notif_channel_enum"), default=NotificationChannel.IN_APP)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    action_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)
