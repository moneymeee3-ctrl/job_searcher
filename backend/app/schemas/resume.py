"""EMBEDHUNT AI — Resume Schemas"""
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ResumeUploadResponse(BaseModel):
    resume_id: str; status: str; skills_count: int
    years_experience: float; is_embedded: bool
    embedded_score: int; top_skills: list[str]
    warnings: list[str]; message: str

class ResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str; name: str; file_name: str; file_type: str
    status: str; is_primary: bool; skill_count: int = 0

class ResumeProfileResponse(BaseModel):
    resume_id: str; name: str; status: str
    total_years_experience: float
    current_role: Optional[str] = None
    current_company: Optional[str] = None
    is_embedded_engineer: bool; embedded_domain_score: int
    programming_languages: list[str] = []
    rtos_and_os: list[str] = []; protocols: list[str] = []
    hardware_platforms: list[str] = []; automotive_safety: list[str] = []
    tools_and_debug: list[str] = []; all_skills: list[str] = []
    highest_degree: str = ""; field_of_study: str = ""
