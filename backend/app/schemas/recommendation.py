"""EMBEDHUNT AI — Recommendation Schemas"""
from typing import Optional
from pydantic import BaseModel

class CategoryScoreOut(BaseModel):
    category: str; weight: int; candidate_skills: list[str]
    job_skills: list[str]; matched_skills: list[str]
    raw_score: float; weighted_score: float

class SkillGapOut(BaseModel):
    skill: str; category: str; priority: str
    learning_resources: list[str]; in_required: bool

class GapAnalysisOut(BaseModel):
    job_title: str; total_score: int; recommendation: str
    high: list[SkillGapOut]; medium: list[SkillGapOut]; low: list[SkillGapOut]
    matched_skills: list[str]; immediate_focus: list[str]
    upskill_weeks: int; summary: str

class RankedJobOut(BaseModel):
    rank: int; job_id: str; title: str; company: str
    company_tier: str; location: str; source_url: str
    apply_url: Optional[str]; salary_min_lpa: Optional[float]
    salary_max_lpa: Optional[float]; meets_salary: bool
    match_score: int; match_tier: str; is_auto_apply: bool
    matched_skills: list[str]; missing_skills: list[str]
    explanation: str; recommendation: str
    category_scores: list[CategoryScoreOut]; gap: GapAnalysisOut

class RankingResultOut(BaseModel):
    candidate: str; total_scanned: int; total_qualified: int
    auto_apply_count: int; strong_count: int
    salary_filter: str; summary: str; jobs: list[RankedJobOut]

class ApproveRequest(BaseModel):
    job_id: str; resume_id: Optional[str] = None
