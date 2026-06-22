"""EMBEDHUNT AI — Dashboard API"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.auth.permissions import get_current_user_id
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/", summary="Full dashboard with metrics, recommendations, and applications")
async def get_dashboard(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await DashboardService(db).get_dashboard(user_id)
