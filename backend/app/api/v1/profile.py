"""EMBEDHUNT AI — Profile API"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.auth.permissions import get_current_user_id
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profile", tags=["Candidate Profile"])

@router.get("/", summary="Get full candidate profile built from primary resume")
async def get_profile(user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    return await ProfileService(db).get_profile_dict(user_id)
