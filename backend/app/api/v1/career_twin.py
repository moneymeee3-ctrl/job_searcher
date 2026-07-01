"""EMBEDHUNT AI — Career Twin API."""
from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.permissions import get_current_user_id
from app.database.session import get_db
from app.services.career_twin_service import CareerTwinService

router = APIRouter(prefix="/career-twin", tags=["Career Twin"])


@router.post("/init", status_code=201, summary="Initialize the Career Twin from a resume")
async def init_twin(
    resume_id: str = Query(..., description="Parsed resume to seed the twin"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    svc = CareerTwinService(db)
    twin = await svc.create_from_resume(user_id, resume_id)
    return svc.to_dict(twin)


@router.get("/", summary="Get the full Career Twin")
async def get_twin(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    svc = CareerTwinService(db)
    return svc.to_dict(await svc.get_twin(user_id))


@router.get("/summary", summary="Dashboard-ready Career Twin summary")
async def get_summary(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await CareerTwinService(db).get_twin_summary(user_id)


@router.get("/weekly-delta", summary="What changed in the Career Twin this week")
async def weekly_delta(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await CareerTwinService(db).get_weekly_delta(user_id)


@router.patch("/skills/{skill_name}", summary="Update the confidence of a single skill")
async def update_skill(
    skill_name: str,
    confidence: float = Query(..., ge=0.0, le=1.0),
    source: str = Query("self_declared"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    svc = CareerTwinService(db)
    twin = await svc.update_skill_confidence(user_id, skill_name, confidence, source)
    return svc.to_dict(twin)


@router.post("/interview-result", status_code=201, summary="Record an interview outcome")
async def interview_result(
    interview_data: dict = Body(...),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    svc = CareerTwinService(db)
    twin = await svc.add_interview_result(user_id, interview_data)
    return svc.to_dict(twin)
