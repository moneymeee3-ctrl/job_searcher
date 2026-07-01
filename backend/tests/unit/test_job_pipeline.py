"""Unit tests for Module 5 — live job pipeline, persistence, scheduler, Naukri."""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database.base import Base
from app.job_sources.base import JobSource
from app.job_sources.naukri import NaukriSource
from app.job_sources.pipeline import JobPipeline, run_pipeline
from app.job_sources.schema import JobPosting
from app.repositories.discovered_job_repository import DiscoveredJobRepository
from app.scheduler.job_scheduler import JobPipelineScheduler

import app.models  # noqa: F401  (register models on Base.metadata)


# ── in-memory DB (shared engine so scheduler sessions see the same data) ──────

@pytest_asyncio.fixture
async def engine():
    eng = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture
async def db(session_factory):
    async with session_factory() as session:
        yield session


# ── fake source ──────────────────────────────────────────────────────────────

class _FakeSource(JobSource):
    def __init__(self, postings):
        self.name = "fake:src"
        self._postings = postings

    def fetch(self, fetcher):
        return self._postings


def _posting(ext_id="1", title="Embedded Firmware Engineer", company="Bosch"):
    return JobPosting(
        external_id=ext_id, title=title, company=company, location="Pune, India",
        apply_url="https://example.com/jobs/1", source_portal="fake:src",
        source_url="https://example.com/jobs/1",
        description="FreeRTOS firmware on ARM Cortex-M with CAN, SPI, I2C. 5 years C.",
    )


# ── pipeline persistence ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_pipeline_persists_new_jobs(db):
    stats = await run_pipeline(db, sources=[_FakeSource([_posting("1"), _posting("2", title="RTOS Engineer")])])
    assert stats.discovered == 2
    assert stats.created == 2
    assert stats.updated == 0
    corpus = await DiscoveredJobRepository(db).get_active_corpus()
    assert len(corpus) == 2


@pytest.mark.asyncio
async def test_pipeline_upsert_is_idempotent(db):
    src = _FakeSource([_posting("1")])
    await JobPipeline(db).run(sources=[src])
    stats2 = await JobPipeline(db).run(sources=[src])
    assert stats2.created == 0
    assert stats2.updated == 1
    assert await DiscoveredJobRepository(db).count_active() == 1


@pytest.mark.asyncio
async def test_pipeline_reports_source_status(db):
    class _Boom(JobSource):
        name = "boom:src"
        def fetch(self, fetcher):
            raise RuntimeError("dead ATS")

    stats = await run_pipeline(db, sources=[_FakeSource([_posting("1")]), _Boom()])
    assert "fake:src" in stats.sources_ok
    assert "boom:src" in stats.sources_failed
    assert stats.created == 1


# ── scheduler ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_scheduler_run_once_tracks_state(session_factory):
    sched = JobPipelineScheduler(session_factory, interval_seconds=999)
    src = _FakeSource([_posting("1")])
    # inject sources via a subclassed run_once path: patch pipeline through run_pipeline
    from app.job_sources import pipeline as pmod
    orig = pmod.run_pipeline

    async def _patched(db, *, fetcher=None, sources=None):
        return await orig(db, fetcher=fetcher, sources=[src])

    import app.scheduler.job_scheduler as smod
    smod.run_pipeline = _patched
    try:
        stats = await sched.run_once()
    finally:
        smod.run_pipeline = orig

    assert stats.created == 1
    assert sched.run_count == 1
    assert sched.last_run_at is not None
    assert sched.last_stats is stats


@pytest.mark.asyncio
async def test_scheduler_run_once_survives_failure(session_factory):
    sched = JobPipelineScheduler(session_factory, interval_seconds=999)
    import app.scheduler.job_scheduler as smod
    orig = smod.run_pipeline

    async def _boom(db, *, fetcher=None, sources=None):
        raise RuntimeError("kaboom")

    smod.run_pipeline = _boom
    try:
        stats = await sched.run_once()
    finally:
        smod.run_pipeline = orig
    assert stats.discovered == 0
    assert sched.run_count == 1


# ── Naukri connector (mocked fetcher) ────────────────────────────────────────

def test_naukri_parses_feed():
    payload = {
        "jobDetails": [
            {
                "jobId": "n1",
                "title": "Embedded C Developer",
                "companyName": "Tata Elxsi",
                "location": "Bangalore",
                "jdURL": "https://www.naukri.com/job-listings-n1",
                "jobDescription": "Firmware in C on ARM with CAN and SPI.",
                "tagsAndSkills": "C,ARM,CAN,SPI",
                "experienceText": "3-6 years",
            }
        ]
    }
    src = NaukriSource("https://partner.example.com/feed")
    postings = src.fetch(lambda url: payload)
    assert len(postings) == 1
    p = postings[0]
    assert p.company == "Tata Elxsi"
    assert p.experience_min == 3
    assert "c" in p.required_skills


def test_naukri_handles_empty():
    src = NaukriSource("https://partner.example.com/feed")
    assert src.fetch(lambda url: {}) == []
