"""EMBEDHUNT AI — Interview API"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.auth.permissions import get_current_user_id
from app.services.interview_service import InterviewService

router = APIRouter(prefix="/interview", tags=["Interview Preparation"])

@router.get("/prep", summary="General interview preparation kit")
async def general_prep(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await InterviewService(db).get_general_prep(user_id)

@router.get("/prep/{job_id}", summary="Interview kit for a specific job")
async def prep_for_job(job_id: str, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await InterviewService(db).get_interview_kit(user_id, job_id)
