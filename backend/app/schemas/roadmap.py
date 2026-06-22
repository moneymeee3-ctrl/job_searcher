"""EMBEDHUNT AI — Roadmap Schemas"""
from typing import Optional
from pydantic import BaseModel

class RoadmapTaskOut(BaseModel):
    skill: str; priority: str; estimated_hours: int
    resources: list[str]; completed: bool = False

class RoadmapOut(BaseModel):
    user_id: str; target_job: str; total_gap_skills: int
    estimated_weeks: int; tasks: list[RoadmapTaskOut]
    score_before: int; score_after_estimated: int
