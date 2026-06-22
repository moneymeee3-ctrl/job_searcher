"""EMBEDHUNT AI — Autonomous Agent API."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.permissions import get_current_user_id
from app.database.session import get_db
from app.services.agent_service import AgentService

router = APIRouter(prefix="/agent", tags=["Autonomous Agent"])


@router.get("/advise", summary="Autonomous career advice: scan, reason, plan, coach")
async def advise(
    min_score: int = Query(40, ge=0, le=99),
    salary_min_lpa: float = Query(15.0, ge=0),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await AgentService(db).advise(user_id, min_score=min_score, salary_min=salary_min_lpa)


@router.post("/auto-apply", status_code=201, summary="Autonomously queue apply-now matches")
async def auto_apply(
    salary_min_lpa: float = Query(15.0, ge=0),
    max_applications: int = Query(5, ge=1, le=20),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await AgentService(db).auto_apply(
        user_id, salary_min=salary_min_lpa, max_applications=max_applications
    )
