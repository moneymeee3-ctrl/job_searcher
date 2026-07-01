"""EMBEDHUNT AI — Career Twin tests (Module 1)."""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database.base import Base
from app.resume.extractor import extract_skills, extract_experience
from app.resume.normalizer import build_profile
from app.services.career_twin_service import CareerTwinService

import app.models  # noqa: F401 — register tables

SAMPLE_RESUME = """
Ram Kumar
ram.kumar@example.com  +91 9876543210

Senior Embedded Software Engineer at Bosch

Experience
Bosch Global Software Technologies  2019 - present
Embedded firmware in C and C++ on ARM Cortex-M. AUTOSAR Classic BSW, CAN, LIN,
SPI, I2C, FreeRTOS, ISO 26262 ASIL-D, MISRA C, device driver development.

Education
B.E. Electronics, 2018
"""


def _profile():
    skills = extract_skills(SAMPLE_RESUME)
    exp = extract_experience(SAMPLE_RESUME)
    return build_profile(SAMPLE_RESUME, skills, exp)


@pytest_asyncio.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with maker() as session:
        yield session
    await engine.dispose()


async def _seed_twin(db) -> CareerTwinService:
    """Create a parsed primary resume, then init the twin from it."""
    from app.models.resume import Resume, ResumeStatus

    resume = Resume(
        user_id="u1", name="cv", file_url="local://x", file_name="cv.txt",
        file_type="txt", is_primary=True, status=ResumeStatus.PARSED,
        ai_summary=_profile().to_json(),
    )
    db.add(resume)
    await db.flush()
    svc = CareerTwinService(db)
    await svc.create_from_resume("u1", resume.id)
    return svc


@pytest.mark.asyncio
async def test_twin_created_with_correct_skill_categories(db):
    svc = await _seed_twin(db)
    twin = await svc.get_twin("u1")
    categories = {s["category"] for s in twin.skills}
    assert "programming" in categories
    assert "protocols" in categories
    assert "automotive" in categories
    names = {s["name"] for s in twin.skills}
    assert "c" in names and "can" in names
    assert all(s["source"] == "resume" for s in twin.skills)
    assert twin.embedded_domain_score > 0


@pytest.mark.asyncio
async def test_update_skill_confidence_updates_confidence_and_recency(db):
    svc = await _seed_twin(db)
    await svc.update_skill_confidence("u1", "AUTOSAR", 0.95, source="self_declared")
    twin = await svc.get_twin("u1")
    skill = next(s for s in twin.skills if s["name"].lower() == "autosar")
    assert skill["confidence"] == 0.95
    assert skill["recency_score"] == 1.0
    assert skill["source"] == "self_declared"


@pytest.mark.asyncio
async def test_update_unknown_skill_adds_it(db):
    svc = await _seed_twin(db)
    await svc.update_skill_confidence("u1", "Rust", 0.5)
    twin = await svc.get_twin("u1")
    assert any(s["name"] == "Rust" for s in twin.skills)


@pytest.mark.asyncio
async def test_confidence_is_clamped(db):
    svc = await _seed_twin(db)
    await svc.update_skill_confidence("u1", "c", 5.0)
    twin = await svc.get_twin("u1")
    assert next(s for s in twin.skills if s["name"] == "c")["confidence"] == 1.0


@pytest.mark.asyncio
async def test_interview_result_records_and_lowers_weak_skill(db):
    svc = await _seed_twin(db)
    before = next(s for s in (await svc.get_twin("u1")).skills if s["name"] == "can")["confidence"]
    await svc.add_interview_result("u1", {
        "company": "Bosch", "role": "Embedded Engineer", "outcome": "rejected",
        "weak_topics": ["can"], "strong_topics": ["c"],
    })
    twin = await svc.get_twin("u1")
    assert len(twin.interview_history) == 1
    assert "can" in twin.known_weaknesses
    assert "c" in twin.strengths
    after = next(s for s in twin.skills if s["name"] == "can")["confidence"]
    assert after < before


@pytest.mark.asyncio
async def test_mark_skill_learned_sets_learned_source(db):
    svc = await _seed_twin(db)
    await svc.mark_skill_learned("u1", "yocto")
    twin = await svc.get_twin("u1")
    skill = next(s for s in twin.skills if s["name"].lower() == "yocto")
    assert skill["source"] == "learned"
    assert skill["confidence"] >= 0.7


@pytest.mark.asyncio
async def test_weekly_delta_returns_recent_changes(db):
    svc = await _seed_twin(db)
    await svc.update_skill_confidence("u1", "c", 0.9)
    delta = await svc.get_weekly_delta("u1")
    fields = {c["field"] for c in delta["changed_fields"]}
    assert "skills" in fields
    assert delta["changed_count"] >= 1


@pytest.mark.asyncio
async def test_weekly_delta_excludes_old_changes(db):
    svc = await _seed_twin(db)
    twin = await svc.get_twin("u1")
    twin.change_log = {"skills": "2000-01-01T00:00:00+00:00"}
    await db.flush()
    delta = await svc.get_weekly_delta("u1")
    assert delta["changed_count"] == 0


@pytest.mark.asyncio
async def test_summary_is_lightweight(db):
    svc = await _seed_twin(db)
    summary = await svc.get_twin_summary("u1")
    assert summary["full_name"]
    assert summary["skill_count"] > 0
    assert "top_skills" in summary
    assert isinstance(summary["interview_readiness_score"], int)


@pytest.mark.asyncio
async def test_reinit_bumps_version(db):
    svc = await _seed_twin(db)
    twin = await svc.get_twin("u1")
    assert twin.version == 1
    await svc.create_from_resume("u1", twin.source_resume_id)
    twin2 = await svc.get_twin("u1")
    assert twin2.version == 2
