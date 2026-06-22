"""EMBEDHUNT AI — Recommendation / Job Match Model"""
from typing import Optional
from sqlalchemy import String, Boolean, Text, Integer, Float, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum
from app.database.base import BaseModel

class MatchTier(str, Enum):
    AUTO_APPLY="auto_apply"; STRONG="strong"; GOOD="good"; PARTIAL="partial"

class JobRecommendation(BaseModel):
    __tablename__ = "job_recommendations"
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    job_id: Mapped[str] = mapped_column(String(200), nullable=False)
    job_title: Mapped[str] = mapped_column(String(300), nullable=False)
    company_name: Mapped[str] = mapped_column(String(200), nullable=False)
    company_tier: Mapped[str] = mapped_column(String(50), default="")
    location: Mapped[str] = mapped_column(String(200), default="")
    source_portal: Mapped[str] = mapped_column(String(100), default="")
    source_url: Mapped[str] = mapped_column(String(1000), default="")
    apply_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    salary_min_lpa: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salary_max_lpa: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    meets_salary_filter: Mapped[bool] = mapped_column(Boolean, default=True)
    match_score: Mapped[int] = mapped_column(Integer, default=0)
    match_tier: Mapped[MatchTier] = mapped_column(SAEnum(MatchTier, name="match_tier_enum"), default=MatchTier.PARTIAL)
    is_auto_apply_candidate: Mapped[bool] = mapped_column(Boolean, default=False)
    matched_skills: Mapped[str] = mapped_column(Text, default="")
    missing_skills: Mapped[str] = mapped_column(Text, default="")
    explanation: Mapped[str] = mapped_column(Text, default="")
    gap_analysis_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_saved: Mapped[bool] = mapped_column(Boolean, default=False)
    scan_run_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
