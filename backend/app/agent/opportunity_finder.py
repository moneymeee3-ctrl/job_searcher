"""EMBEDHUNT AI — Opportunity Finder.

Proactively scans the job market for a candidate and classifies every qualifying
role into actionable buckets. Embodies the product's core principle: *do not wait
for the user to ask* — surface apply-now roles, strong fits and stretch goals
automatically.

Today this scans the recommendation engine's corpus. The same interface will
back live ``job_sources`` connectors without changing any downstream agent code.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.recommendation.engine import run_matching
from app.recommendation.ranking import RankedJob, RankingResult
from app.resume.normalizer import CandidateProfile


@dataclass
class Opportunity:
    job_id: str
    title: str
    company: str
    company_tier: str
    location: str
    apply_url: str | None
    source_portal: str
    salary_min_lpa: float | None
    salary_max_lpa: float | None
    meets_salary: bool
    match_score: int
    match_tier: str
    is_auto_apply: bool
    bucket: str                       # apply_now | strong | stretch
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "title": self.title,
            "company": self.company,
            "company_tier": self.company_tier,
            "location": self.location,
            "apply_url": self.apply_url,
            "source_portal": self.source_portal,
            "salary_min_lpa": self.salary_min_lpa,
            "salary_max_lpa": self.salary_max_lpa,
            "meets_salary": self.meets_salary,
            "match_score": self.match_score,
            "match_tier": self.match_tier,
            "is_auto_apply": self.is_auto_apply,
            "bucket": self.bucket,
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
        }


@dataclass
class OpportunityScan:
    result: RankingResult
    opportunities: list[Opportunity] = field(default_factory=list)

    @property
    def apply_now(self) -> list[Opportunity]:
        return [o for o in self.opportunities if o.bucket == "apply_now"]

    @property
    def strong(self) -> list[Opportunity]:
        return [o for o in self.opportunities if o.bucket == "strong"]

    @property
    def stretch(self) -> list[Opportunity]:
        return [o for o in self.opportunities if o.bucket == "stretch"]


def _bucket(job: RankedJob) -> str:
    if job.is_auto_apply:
        return "apply_now"
    if job.match_score >= 70:
        return "strong"
    return "stretch"


def _to_opportunity(job: RankedJob) -> Opportunity:
    return Opportunity(
        job_id=job.job_id,
        title=job.title,
        company=job.company,
        company_tier=job.company_tier,
        location=job.location,
        apply_url=job.apply_url,
        source_portal=job.source_portal,
        salary_min_lpa=job.salary_min_lpa,
        salary_max_lpa=job.salary_max_lpa,
        meets_salary=job.meets_salary,
        match_score=job.match_score,
        match_tier=job.match_tier.value,
        is_auto_apply=job.is_auto_apply,
        bucket=_bucket(job),
        matched_skills=job.match.matched_skills,
        missing_skills=job.match.missing_skills,
    )


def find_opportunities(
    profile: CandidateProfile,
    *,
    min_score: int = 40,
    salary_min: float = 15.0,
    result: RankingResult | None = None,
) -> OpportunityScan:
    """Scan the market and bucket every qualifying role.

    ``result`` may be supplied to avoid recomputation (and to keep this pure for
    tests); otherwise the recommendation engine is run.
    """
    if result is None:
        result = run_matching(profile, min_score=min_score, salary_min=salary_min)
    opportunities = [_to_opportunity(j) for j in result.jobs]
    return OpportunityScan(result=result, opportunities=opportunities)
