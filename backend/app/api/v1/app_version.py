from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.logging import get_logger
from app.config.settings import settings
from app.database.session import get_db
from app.models.app_version import AppVersion

logger = get_logger(__name__)

router = APIRouter(prefix="/app", tags=["App Update"])


class PublishVersion(BaseModel):
    latest_version: str
    version_code: int = Field(..., ge=1)
    apk_url: str
    minimum_version: str = "1.0.0"
    force_update: bool = False
    release_notes: list[str] = Field(default_factory=list)


@router.get("/version")
async def get_version(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AppVersion).limit(1))
    version = result.scalar_one_or_none()

    if version is None:
        version = AppVersion()
        db.add(version)
        await db.commit()
        await db.refresh(version)

    return {
        "latest_version": version.latest_version,
        "version_code": version.version_code,
        "apk_url": version.apk_url,
        "minimum_version": version.minimum_version,
        "force_update": version.force_update,
        "release_notes": version.release_notes,
        "released_at": version.released_at.isoformat()
        if version.released_at
        else "",
    }


@router.post("/version/update")
async def publish_version(
    payload: PublishVersion,
    x_update_secret: str | None = Header(None, alias="X-Update-Secret"),
    db: AsyncSession = Depends(get_db),
):
    logger.info(
        "update_secret_check",
        header_present=x_update_secret is not None,
        env_present=bool(settings.APP_UPDATE_SECRET),
        matches=x_update_secret == settings.APP_UPDATE_SECRET,
    )

    if x_update_secret != settings.APP_UPDATE_SECRET:
        logger.warning("mobile_version_publish_denied")
        raise HTTPException(403, "Invalid update secret")

    result = await db.execute(select(AppVersion).limit(1))
    version = result.scalar_one_or_none()

    if version is None:
        version = AppVersion()
        db.add(version)

    version.latest_version = payload.latest_version
    version.version_code = payload.version_code
    version.apk_url = payload.apk_url
    version.minimum_version = payload.minimum_version
    version.force_update = payload.force_update
    version.release_notes = payload.release_notes
    version.released_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(version)

    return {
        "success": True,
        "data": {
            "latest_version": version.latest_version,
            "version_code": version.version_code,
            "apk_url": version.apk_url,
            "minimum_version": version.minimum_version,
            "force_update": version.force_update,
            "release_notes": version.release_notes,
            "released_at": version.released_at.isoformat(),
        },
    }