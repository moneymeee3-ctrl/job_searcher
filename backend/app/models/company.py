"""EMBEDHUNT AI — Company Model"""
from typing import Optional
from sqlalchemy import String, Boolean, Text, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import BaseModel

class Company(BaseModel):
    __tablename__ = "companies"
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    tier: Mapped[str] = mapped_column(String(50), default="other")
    careers_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    company_size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    headquarters: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    tech_stack: Mapped[Optional[str]] = mapped_column(Text, nullable=True)      # JSON list
    embedded_domains: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avg_salary_min_lpa: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_salary_max_lpa: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    interview_difficulty: Mapped[str] = mapped_column(String(20), default="medium")
    priority_score: Mapped[int] = mapped_column(Integer, default=50)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Feedback intelligence
    call_rate: Mapped[float] = mapped_column(Float, default=0.0)  # % of apps that got a call
    offer_rate: Mapped[float] = mapped_column(Float, default=0.0)
    total_applications_sent: Mapped[int] = mapped_column(Integer, default=0)
    total_interviews: Mapped[int] = mapped_column(Integer, default=0)
