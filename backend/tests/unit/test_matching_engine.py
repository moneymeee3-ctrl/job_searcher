"""Unit tests for Module 4 — unified matching engine."""
import pytest

from app.ai.embeddings import EmbeddingEngine
from app.ai.matching_engine import MatchingEngine, UnifiedMatch, get_matching_engine
from app.ai.semantic_engine import SemanticMatchEngine
from app.recommendation.ranking import MatchTier
from app.resume.normalizer import CandidateProfile


@pytest.fixture
def engine():
    sem = SemanticMatchEngine(engine=EmbeddingEngine(use_model=False))
    return MatchingEngine(semantic=sem)


def _profile() -> CandidateProfile:
    return CandidateProfile(
        total_years_experience=6.0,
        is_embedded_engineer=True,
        programming_languages=["c", "c++"],
        rtos_and_os=["freertos"],
        protocols=["can", "spi", "i2c"],
        hardware_platforms=["arm", "stm32", "cortex-m4"],
        automotive_safety=["autosar", "iso 26262"],
        tools_and_debug=["jtag", "gdb", "git"],
        software_concepts=["device driver"],
    )


JOBS = [
    {"id": "match", "title": "Embedded Firmware Engineer", "company": "Bosch",
     "description": "FreeRTOS firmware on ARM Cortex-M with CAN, SPI, I2C, AUTOSAR.",
     "required_skills": "c,c++,freertos,can,spi,i2c,arm,autosar",
     "experience_min": 4, "salary_min_lpa": 20.0, "salary_max_lpa": 35.0},
    {"id": "web", "title": "React Frontend Developer", "company": "WebCo",
     "description": "React, TypeScript, CSS.", "required_skills": "react,typescript,css",
     "experience_min": 3, "salary_min_lpa": 18.0, "salary_max_lpa": 25.0},
]


def test_match_returns_unified(engine):
    m = engine.match(_profile(), JOBS[0])
    assert isinstance(m, UnifiedMatch)
    assert 0 <= m.total_score <= 99
    assert m.keyword_score >= 0 and m.semantic_score >= 0


def test_rank_orders_relevant_first(engine):
    ranked = engine.rank_jobs(_profile(), JOBS, min_score=0)
    assert ranked[0].job_id == "match"
    assert ranked[0].total_score > ranked[-1].total_score
    assert ranked[0].rank == 1


def test_min_score_filter(engine):
    ranked = engine.rank_jobs(_profile(), JOBS, min_score=95)
    assert all(m.total_score >= 95 for m in ranked)


def test_confidence_factor_scales_score(engine):
    profile = _profile()
    high = engine.match(profile, JOBS[0],
                        skill_confidence={s: 1.0 for s in ["c", "c++", "freertos", "can", "spi", "i2c", "arm", "autosar"]})
    low = engine.match(profile, JOBS[0],
                       skill_confidence={s: 0.0 for s in ["c", "c++", "freertos", "can", "spi", "i2c", "arm", "autosar"]})
    assert high.confidence_factor > low.confidence_factor
    assert high.total_score >= low.total_score


def test_confidence_factor_defaults_to_one(engine):
    m = engine.match(_profile(), JOBS[0])
    assert m.confidence_factor == 1.0


def test_tier_assigned(engine):
    m = engine.match(_profile(), JOBS[0])
    assert m.tier in set(MatchTier)


def test_singleton_accessor():
    assert get_matching_engine() is get_matching_engine()
