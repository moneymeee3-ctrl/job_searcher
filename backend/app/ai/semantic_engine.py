"""EMBEDHUNT AI — Semantic matching engine.

Combines the deterministic keyword matcher with semantic similarity signals:

    final = keyword * 0.55 + semantic_skill * 0.25 + semantic_alignment * 0.20

then applies a missing-skill penalty, an experience multiplier, and calibration
caps (so pure-semantic overlap can't fake a strong match). Degrades gracefully
to keyword-only scoring if embeddings are unavailable.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.ai.embeddings import EmbeddingEngine, get_embedding_engine
from app.recommendation.matcher import compute_match
from app.resume.normalizer import CandidateProfile

_PROFILE_ATTRS = [
    "programming_languages", "rtos_and_os", "protocols", "hardware_platforms",
    "automotive_safety", "tools_and_debug", "software_concepts",
]


@dataclass
class SemanticMatch:
    total_score: int
    keyword_score: float
    semantic_skill_score: float
    alignment_score: float
    experience_multiplier: float
    missing_penalty: float
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    recommendation: str = ""
    method: str = "semantic"


def _profile_skills(profile: CandidateProfile) -> list[str]:
    out: list[str] = []
    for attr in _PROFILE_ATTRS:
        out.extend(getattr(profile, attr, []) or [])
    return sorted({s.lower() for s in out if s})


class SemanticMatchEngine:
    KEYWORD_W = 0.55
    SEMANTIC_SKILL_W = 0.25
    ALIGNMENT_W = 0.20

    def __init__(self, engine: EmbeddingEngine | None = None):
        self.engine = engine or get_embedding_engine()

    def score(self, profile: CandidateProfile, title: str, description: str | None,
              required_skills: str | None, exp_min: int | None = None,
              exp_max: int | None = None) -> SemanticMatch:
        km = compute_match(profile, title, description, required_skills, exp_min, exp_max)
        keyword_score = km.total_score / 99.0
        cand_skills = _profile_skills(profile)
        job_skills = sorted({s.lower() for s in km.job_required_skills if s})

        try:
            semantic_skill = self._semantic_skill_score(cand_skills, job_skills)
            alignment = self._alignment_score(cand_skills, title, description)
            method = "semantic"
        except Exception:
            semantic_skill = alignment = 0.0
            method = "keyword_fallback"

        combined = (keyword_score * self.KEYWORD_W
                    + semantic_skill * self.SEMANTIC_SKILL_W
                    + alignment * self.ALIGNMENT_W)

        missing_penalty = self._missing_penalty(km.missing_skills, job_skills)
        exp_mult = self._experience_multiplier(profile, exp_min)
        combined = combined * (1.0 - missing_penalty) * exp_mult
        final = self._calibrate(combined, keyword_score, semantic_skill)

        total = max(0, min(99, int(round(final * 100))))
        recommendation = ("strong_match" if total >= 85 else "good_match" if total >= 70
                          else "partial_match" if total >= 50 else "low_match")
        return SemanticMatch(
            total_score=total,
            keyword_score=round(keyword_score, 4),
            semantic_skill_score=round(semantic_skill, 4),
            alignment_score=round(alignment, 4),
            experience_multiplier=round(exp_mult, 3),
            missing_penalty=round(missing_penalty, 3),
            matched_skills=km.matched_skills,
            missing_skills=km.missing_skills,
            recommendation=recommendation,
            method=method,
        )

    # ---- components ----
    def _semantic_skill_score(self, cand_skills, job_skills) -> float:
        if not job_skills or not cand_skills:
            return 0.0
        cand_vecs = self.engine.embed_batch(cand_skills)
        total = 0.0
        for js in job_skills:
            jv = self.engine.embed_text(js)
            best = max((self.engine.cosine_similarity(jv, cv) for cv in cand_vecs), default=0.0)
            total += best
        return total / len(job_skills)

    def _alignment_score(self, cand_skills, title, description) -> float:
        cand_text = ", ".join(cand_skills)
        job_text = " ".join(filter(None, [title, description]))
        if not cand_text or not job_text:
            return 0.0
        return self.engine.cosine_similarity(
            self.engine.embed_text(cand_text), self.engine.embed_text(job_text))

    @staticmethod
    def _missing_penalty(missing, job_skills) -> float:
        if not job_skills:
            return 0.0
        frac = len(missing) / len(job_skills)
        return min(0.20, frac * 0.20)

    @staticmethod
    def _experience_multiplier(profile: CandidateProfile, exp_min: int | None) -> float:
        if not exp_min:
            return 1.0
        yrs = profile.total_years_experience or 0.0
        if yrs >= exp_min:
            return 1.0
        if yrs >= exp_min * 0.75:
            return 0.95
        if yrs >= exp_min * 0.5:
            return 0.88
        return 0.80

    @staticmethod
    def _calibrate(combined: float, keyword_score: float, semantic_skill: float) -> float:
        cap = 0.99
        if keyword_score < 0.15:
            cap = min(cap, 0.60)
        if semantic_skill < 0.20:
            cap = min(cap, 0.85)
        return max(0.0, min(cap, combined))


_default_semantic: SemanticMatchEngine | None = None


def get_semantic_engine() -> SemanticMatchEngine:
    global _default_semantic
    if _default_semantic is None:
        _default_semantic = SemanticMatchEngine()
    return _default_semantic
