from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import BaseModel


class AppVersion(BaseModel):
    __tablename__ = "app_versions"

    latest_version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="1.0.0",
    )

    version_code: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=10000,
    )

    apk_url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        default="",
    )

    minimum_version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="1.0.0",
    )

    force_update: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    release_notes: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    released_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )