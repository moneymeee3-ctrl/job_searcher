"""EMBEDHUNT AI — Learning Roadmap Model"""
from typing import Optional
from sqlalchemy import String, Boolean, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import BaseModel

class LearningRoadmap(BaseModel):
    __tablename__ = "learning_roadmaps"
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    target_job_title: Mapped[str] = mapped_column(String(300), nullable=False)
    target_company: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    score_before: Mapped[int] = mapped_column(Integer, default=0)
    score_after_estimated: Mapped[int] = mapped_column(Integer, default=0)
    total_gap_skills: Mapped[int] = mapped_column(Integer, default=0)
    estimated_weeks: Mapped[int] = mapped_column(Integer, default=0)
    tasks_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)   # JSON list of tasks
    completed_skills: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list
    progress_pct: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
