"""EMBEDHUNT AI — Resume Model"""
from typing import Optional
from sqlalchemy import String, Boolean, Text, Integer, Float, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum
from app.database.base import BaseModel

class ResumeStatus(str, Enum):
    UPLOADED="uploaded"; PARSING="parsing"; PARSED="parsed"
    PARSE_FAILED="parse_failed"; EMBEDDING_READY="embedding_ready"

class Resume(BaseModel):
    __tablename__ = "resumes"
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    file_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_name: Mapped[str] = mapped_column(String(300), nullable=False)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_type: Mapped[str] = mapped_column(String(50), default="pdf")
    status: Mapped[ResumeStatus] = mapped_column(SAEnum(ResumeStatus, name="resume_status_enum"), default=ResumeStatus.UPLOADED)
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parsed_skills: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parsed_experience: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parsed_education: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parsed_projects: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    skill_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    embedding_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_embedding_ready: Mapped[bool] = mapped_column(Boolean, default=False)
    is_auto_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    generated_for_job_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
