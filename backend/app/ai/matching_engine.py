"""EMBEDHUNT AI — Unified matching engine (Module 4).

Blends three signals into a single job match score:
  * keyword overlap        — deterministic category matcher
  * semantic similarity    — MiniLM/offline embedding engine
  * skill confidence       — CareerTwin / resume-derived per-skill confidence

Produces ranked, tiered results reusing the existing MatchTier + gap analysis.
Additive: does not alter the legacy keyword-only ranking path.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.ai.semantic_engine import SemanticMatchEngine, get_semantic_engine
from app.recommendation.explain import GapAnalysis, analyze_gaps
from app.recommendation.matcher import MatchScore, compute_match
from app.recommendation.ranking import MatchTier, _meets_salary, _tier
from app.resume.normalizer import CandidateProfile


@dataclass
class UnifiedMatch:
    rank: int
    job_id: str
    title: str
    company: str
    total_score: int
    tier: MatchTier
    keyword_score: int
    semantic_score: int
    confidence_factor: float
    meets_salary: bool
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    explanation: str = ""
    match: MatchScore | None = None
    gap: GapAnalysis | None = None


class MatchingEngine:
    """Orchestrates keyword + semantic + confidence scoring across a corpus."""

    # blend of the semantic-composite score with the confidence factor
    CONFIDENCE_MIN = 0.85  # floor so unknown-confidence skills aren't over-penalised

    def __init__(self, semantic: SemanticMatchEngine | None = None):
        self.semantic = semantic or get_semantic_engine()

    def match(self, profile: CandidateProfile, job: dict,
              skill_confidence: dict[str, float] | None = None) -> UnifiedMatch:
        title = job.get("title", "")
        desc = job.get("description")
        req = job.get("required_skills")
        exp_min, exp_max = job.get("experience_min"), job.get("experience_max")

        km = compute_match(profile, title, desc, req, exp_min, exp_max)
        sm = self.semantic.score(profile, title, desc, req, exp_min, exp_max)

        factor = self._confidence_factor(km.matched_skills, skill_confidence)
        total = max(0, min(99, int(round(sm.total_score * factor))))

        sal_min, sal_max = job.get("salary_min_lpa"), job.get("salary_max_lpa")
        meets = _meets_salary(sal_min, sal_max, job.get("_salary_min", 0.0))
        tier = _tier(total, meets)
        gap = analyze_gaps(km, title)

        return UnifiedMatch(
            rank=0,
            job_id=job.get("id", ""),
            title=title,
            company=job.get("company", ""),
            total_score=total,
            tier=tier,
            keyword_score=km.total_score,
            semantic_score=sm.total_score,
            confidence_factor=round(factor, 3),
            meets_salary=meets,
            matched_skills=km.matched_skills,
            missing_skills=km.missing_skills,
            explanation=km.explanation,
            match=km,
            gap=gap,
        )

    def rank_jobs(self, profile: CandidateProfile, jobs: list[dict],
                  min_score: int = 40, salary_min: float = 15.0,
                  skill_confidence: dict[str, float] | None = None) -> list[UnifiedMatch]:
        results: list[UnifiedMatch] = []
        for job in jobs:
            job = {**job, "_salary_min": salary_min}
            m = self.match(profile, job, skill_confidence)
            if m.total_score < min_score:
                continue
            results.append(m)
        results.sort(key=lambda m: (m.tier != MatchTier.AUTO_APPLY,
                                    not m.meets_salary, -m.total_score))
        for i, m in enumerate(results, 1):
            m.rank = i
        return results

    def _confidence_factor(self, matched_skills: list[str],
                           skill_confidence: dict[str, float] | None) -> float:
        if not skill_confidence or not matched_skills:
            return 1.0
        vals = [skill_confidence.get(s.lower()) for s in matched_skills]
        vals = [v for v in vals if v is not None]
        if not vals:
            return 1.0
        avg = sum(vals) / len(vals)
        # map avg confidence [0,1] onto [CONFIDENCE_MIN, 1.0]
        return self.CONFIDENCE_MIN + (1.0 - self.CONFIDENCE_MIN) * max(0.0, min(1.0, avg))


_default_engine: MatchingEngine | None = None


def get_matching_engine() -> MatchingEngine:
    global _default_engine
    if _default_engine is None:
        _default_engine = MatchingEngine()
    return _default_engine
