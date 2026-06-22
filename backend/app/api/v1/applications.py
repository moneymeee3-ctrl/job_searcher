"""EMBEDHUNT AI — Applications API"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.auth.permissions import get_current_user_id
from app.repositories.application_repository import ApplicationRepository

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.get("/", summary="List all applications")
async def list_apps(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    apps = await ApplicationRepository(db).get_by_user(user_id)
    return [{"id": a.id, "job": a.job_title, "company": a.company_name, "score": a.match_score,
             "status": a.status.value, "outcome": a.outcome.value,
             "salary": f"{a.salary_min_lpa}-{a.salary_max_lpa} LPA" if a.salary_min_lpa else "Not disclosed",
             "approved_at": a.approved_at} for a in apps]
