"""EMBEDHUNT AI — Interview Schemas"""
from pydantic import BaseModel

class InterviewQuestionOut(BaseModel):
    question: str; category: str; difficulty: str
    hint: Optional[str] = None; tags: list[str] = []
    from typing import Optional

class InterviewPrep(BaseModel):
    job_title: str; company: str; readiness_score: int
    questions: list[InterviewQuestionOut]
    coding_topics: list[str]; checklist: list[str]
    estimated_prep_days: int
