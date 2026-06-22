"""EMBEDHUNT AI — Dashboard Schemas"""
from pydantic import BaseModel

class DashboardMetrics(BaseModel):
    profile_score: int; total_applications: int; interviews: int
    offers: int; conversion_rate: float; avg_match_score: float
    auto_apply_ready: int; skills_count: int; learning_progress: int

class ApplicationCardOut(BaseModel):
    id: str; job_title: str; company_name: str; match_score: int
    status: str; outcome: str; applied_at: str = ""
    salary_range: str = ""; location: str = ""
