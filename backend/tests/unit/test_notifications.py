"""EMBEDHUNT AI — Notification platform tests (real persistence over SQLite)."""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database.base import Base
from app.models.notification import NotificationType
from app.services.notification_service import NotificationService

# Ensure all models are registered on Base.metadata before create_all.
import app.models  # noqa: F401


@pytest_asyncio.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with maker() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_create_and_read_job_match(db):
    svc = NotificationService(db)
    created = await svc.create_job_match_notification("u1", "Embedded Engineer", "NVIDIA", 88)
    assert created["type"] == NotificationType.NEW_JOB_MATCH.value
    assert created["is_read"] is False

    feed = await svc.get_notifications("u1")
    assert feed["total"] == 1
    assert feed["unread_count"] == 1
    assert feed["notifications"][0]["metadata"]["score"] == 88


@pytest.mark.asyncio
async def test_mark_read_and_unread_filter(db):
    svc = NotificationService(db)
    await svc.create_application_update("u1", "Firmware Dev", "queued")
    await svc.create_application_update("u1", "RTOS Engineer", "queued")

    feed = await svc.get_notifications("u1")
    assert feed["unread_count"] == 2
    first_id = feed["notifications"][0]["id"]

    result = await svc.mark_read("u1", first_id)
    assert result["updated"] is True

    unread = await svc.get_notifications("u1", unread_only=True)
    assert unread["total"] == 1
    assert unread["unread_count"] == 1


@pytest.mark.asyncio
async def test_mark_all_read(db):
    svc = NotificationService(db)
    await svc.create_job_match_notification("u2", "A", "B", 70)
    await svc.create_job_match_notification("u2", "C", "D", 75)
    res = await svc.mark_all_read("u2")
    assert res["updated"] == 2
    assert (await svc.get_notifications("u2"))["unread_count"] == 0


@pytest.mark.asyncio
async def test_user_isolation(db):
    svc = NotificationService(db)
    await svc.create_job_match_notification("alice", "A", "B", 70)
    await svc.create_job_match_notification("bob", "C", "D", 75)
    assert (await svc.get_notifications("alice"))["total"] == 1
    assert (await svc.get_notifications("bob"))["total"] == 1
