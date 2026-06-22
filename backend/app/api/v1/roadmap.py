"""EMBEDHUNT AI — Roadmap API"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.auth.permissions import get_current_user_id
from app.services.roadmap_service import RoadmapService

router = APIRouter(prefix="/roadmap", tags=["Learning Roadmap"])

@router.get("/", summary="General learning roadmap based on top matched jobs")
async def get_general(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await RoadmapService(db).get_general_roadmap(user_id)

@router.get("/job/{job_id}", summary="Roadmap for a specific job")
async def get_for_job(job_id: str, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await RoadmapService(db).get_roadmap_for_job(user_id, job_id)
