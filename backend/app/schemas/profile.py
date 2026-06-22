"""EMBEDHUNT AI — Profile Schemas"""
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str; user_id: str; headline: str; summary: str
    total_experience_years: float; profile_score: int
    is_actively_looking: bool; preferred_locations: list[str] = []
    min_salary_lpa: float; skills: list[str] = []
    current_role: Optional[str] = None; current_company: Optional[str] = None

class ProfileUpdateRequest(BaseModel):
    headline: Optional[str] = None; summary: Optional[str] = None
    is_actively_looking: Optional[bool] = None
    preferred_locations: Optional[list[str]] = None
    min_salary_lpa: Optional[float] = None
