"""EMBEDHUNT AI — Company Schemas"""
from typing import Optional
from pydantic import BaseModel

class CompanyIntelligenceOut(BaseModel):
    name: str; tier: str; careers_url: str; priority: int

class CompanyFitOut(BaseModel):
    company: str; fit_score: int; matched_tech: list[str]
    missing_tech: list[str]; interview_difficulty: str
    avg_salary_lpa: str; preparation_tips: list[str]
