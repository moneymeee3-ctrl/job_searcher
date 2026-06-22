"""EMBEDHUNT AI — Ranking Engine"""
from dataclasses import dataclass, field
from enum import Enum
from app.recommendation.matcher import MatchScore, compute_match
from app.recommendation.explain import GapAnalysis, analyze_gaps
from app.resume.normalizer import CandidateProfile

class MatchTier(str, Enum):
    AUTO_APPLY="auto_apply"; STRONG="strong"; GOOD="good"; PARTIAL="partial"

@dataclass
class RankedJob:
    rank: int; job_id: str; title: str; company: str; company_tier: str
    location: str; source_portal: str; source_url: str; apply_url: str|None
    salary_min_lpa: float|None; salary_max_lpa: float|None; meets_salary: bool
    match_score: int; match_tier: MatchTier; is_auto_apply: bool
    match: MatchScore; gap: GapAnalysis

@dataclass
class RankingResult:
    candidate: str; total_scanned: int; total_qualified: int
    auto_apply_count: int; strong_count: int
    salary_filter: str; summary: str
    jobs: list[RankedJob] = field(default_factory=list)

def _meets_salary(sal_min, sal_max, required) -> bool:
    if sal_max is not None and sal_max >= required: return True
    if sal_min is not None and sal_min >= required: return True
    return sal_min is None and sal_max is None

def _tier(score: int, meets: bool) -> MatchTier:
    if score >= 85 and meets: return MatchTier.AUTO_APPLY
    if score >= 70: return MatchTier.STRONG
    if score >= 55: return MatchTier.GOOD
    return MatchTier.PARTIAL

def rank_jobs(profile: CandidateProfile, jobs: list[dict], min_score: int=40, salary_min: float=15.0) -> RankingResult:
    ranked = []
    for job in jobs:
        match = compute_match(profile, job.get("title",""), job.get("description"), job.get("required_skills"), job.get("experience_min"), job.get("experience_max"))
        if match.total_score < min_score: continue
        sal_min_j, sal_max_j = job.get("salary_min_lpa"), job.get("salary_max_lpa")
        meets = _meets_salary(sal_min_j, sal_max_j, salary_min)
        tier = _tier(match.total_score, meets)
        gap = analyze_gaps(match, job.get("title",""))
        ranked.append(RankedJob(0, job.get("id",""), job.get("title",""), job.get("company",""), job.get("company_tier",""), job.get("location",""), job.get("source_portal",""), job.get("source_url",""), job.get("apply_url"), sal_min_j, sal_max_j, meets, match.total_score, tier, match.total_score>=85 and meets, match, gap))
    ranked.sort(key=lambda j: (not j.is_auto_apply, not j.meets_salary, -j.match_score))
    for i,j in enumerate(ranked,1): j.rank = i
    auto = sum(1 for j in ranked if j.is_auto_apply)
    strong = sum(1 for j in ranked if j.match_tier == MatchTier.STRONG)
    return RankingResult(profile.name_hint or "Candidate", len(jobs), len(ranked), auto, strong, f"≥{salary_min} LPA", f"Scanned {len(jobs)} → {len(ranked)} qualified. {auto} auto-apply.", ranked)
