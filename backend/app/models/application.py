"""EMBEDHUNT AI — Application Model"""
from typing import Optional
from sqlalchemy import String, Boolean, Text, Integer, Float, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum
from app.database.base import BaseModel

class ApplicationStatus(str, Enum):
    APPROVED="approved"; QUEUED="queued"; APPLYING="applying"
    SUBMITTED="submitted"; FAILED="failed"; WITHDRAWN="withdrawn"; RESPONDED="responded"

class ApplicationOutcome(str, Enum):
    PENDING="pending"; SHORTLISTED="shortlisted"; INTERVIEW="interview"
    OFFER="offer"; REJECTED="rejected"; GHOSTED="ghosted"

class Application(BaseModel):
    __tablename__ = "applications"
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    job_id: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    resume_id: Mapped[str] = mapped_column(String(36), nullable=False)
    job_title: Mapped[str] = mapped_column(String(300), nullable=False)
    company_name: Mapped[str] = mapped_column(String(200), nullable=False)
    company_tier: Mapped[str] = mapped_column(String(50), default="")
    location: Mapped[str] = mapped_column(String(200), default="")
    apply_url: Mapped[str] = mapped_column(String(1000), default="")
    source_portal: Mapped[str] = mapped_column(String(100), default="")
    salary_min_lpa: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salary_max_lpa: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    match_score: Mapped[int] = mapped_column(Integer, default=0)
    matched_skills: Mapped[str] = mapped_column(Text, default="")
    missing_skills: Mapped[str] = mapped_column(Text, default="")
    ai_explanation: Mapped[str] = mapped_column(Text, default="")
    resume_version_name: Mapped[str] = mapped_column(String(200), default="")
    cover_letter: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[ApplicationStatus] = mapped_column(SAEnum(ApplicationStatus, name="app_status_enum"), default=ApplicationStatus.APPROVED)
    outcome: Mapped[ApplicationOutcome] = mapped_column(SAEnum(ApplicationOutcome, name="app_outcome_enum"), default=ApplicationOutcome.PENDING)
    approved_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    submitted_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    responded_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    apply_attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confirmation_number: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
