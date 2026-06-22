"""EMBEDHUNT AI — Recommendation API"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.auth.permissions import get_current_user_id
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["AI Recommendations"])

@router.get("/jobs", summary="Get AI-ranked jobs for your profile")
async def get_jobs(
    min_score: int = Query(40, ge=0, le=99),
    salary_min_lpa: float = Query(15.0, ge=0),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await RecommendationService(db).get_recommendations(user_id, min_score, salary_min_lpa)

@router.get("/jobs/{job_id}/gaps", summary="Full skill gap analysis for a job")
async def get_gaps(job_id: str, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await RecommendationService(db).get_job_gaps(user_id, job_id)

@router.post("/approve", status_code=201, summary="Approve a job for auto-apply")
async def approve(job_id: str, resume_id: str | None = None, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    app = await RecommendationService(db).approve_apply(user_id, job_id, resume_id)
    return {"application_id": app.id, "job": app.job_title, "company": app.company_name, "status": app.status.value, "match_score": app.match_score}
