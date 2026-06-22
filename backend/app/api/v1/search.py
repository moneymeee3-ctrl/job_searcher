"""EMBEDHUNT AI — Search API"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.auth.permissions import get_current_user_id
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/search", tags=["Job Search"])

@router.get("/jobs", summary="Search and filter jobs")
async def search_jobs(
    keyword: str = Query("", description="Job title or skill keyword"),
    location: str = Query("", description="City or 'Remote'"),
    salary_min: float = Query(15.0, description="Minimum salary LPA"),
    min_score: int = Query(40, ge=0, le=99, description="Minimum match score"),
    company_tier: str = Query("", description="tier1_semiconductor, tier2_automotive, etc."),
    sort_by: str = Query("score", description="score | salary | company"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    svc = RecommendationService(db)
    data = await svc.get_recommendations(user_id, min_score, salary_min)
    jobs = data.get("jobs", [])
    if keyword:
        kw = keyword.lower()
        jobs = [j for j in jobs if kw in j["title"].lower() or kw in j["company"].lower()]
    if location:
        jobs = [j for j in jobs if location.lower() in j["location"].lower()]
    if company_tier:
        jobs = [j for j in jobs if j["company_tier"] == company_tier]
    if sort_by == "salary":
        jobs = sorted(jobs, key=lambda j: j.get("salary_max_lpa") or 0, reverse=True)
    elif sort_by == "company":
        jobs = sorted(jobs, key=lambda j: j["company"])
    total = len(jobs)
    start = (page - 1) * page_size
    return {"total": total, "page": page, "page_size": page_size, "has_next": start + page_size < total, "jobs": jobs[start:start + page_size]}
