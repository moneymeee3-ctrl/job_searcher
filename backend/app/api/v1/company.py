"""EMBEDHUNT AI — Company Intelligence API"""
from fastapi import APIRouter, Query
from app.services.company_service import CompanyService

router = APIRouter(prefix="/company", tags=["Company Intelligence"])

@router.get("/intelligence", summary="All monitored companies and portals")
async def get_intelligence():
    return CompanyService().get_intelligence_report()

@router.get("/fit", summary="Company fit analysis")
async def get_fit(company: str = Query(...), score: int = Query(50), skills: str = Query("")):
    skill_list = [s.strip() for s in skills.split(",") if s.strip()]
    return CompanyService().get_company_fit(company, skill_list, score)
