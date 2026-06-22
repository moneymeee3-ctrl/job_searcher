"""EMBEDHUNT AI — Interview Preparation Model"""
from typing import Optional
from sqlalchemy import String, Boolean, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import BaseModel

class InterviewSession(BaseModel):
    __tablename__ = "interview_sessions"
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    job_title: Mapped[str] = mapped_column(String(300), nullable=False)
    company: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    application_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    readiness_score: Mapped[int] = mapped_column(Integer, default=0)
    questions_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    coding_topics: Mapped[Optional[str]] = mapped_column(Text, nullable=True)   # JSON list
    checklist_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list
    estimated_prep_days: Mapped[int] = mapped_column(Integer, default=14)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
