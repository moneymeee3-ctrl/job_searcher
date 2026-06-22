"""EMBEDHUNT AI — Profile Service"""
import json
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.resume_repository import ResumeRepository
from app.resume.normalizer import CandidateProfile

class ProfileService:
    def __init__(self, db: AsyncSession):
        self.repo = ResumeRepository(db)

    async def get_candidate_profile(self, user_id: str) -> CandidateProfile:
        resume = await self.repo.get_primary(user_id)
        if not resume:
            return CandidateProfile()
        if not resume.ai_summary:
            return CandidateProfile()
        try:
            return CandidateProfile.from_json(resume.ai_summary)
        except Exception:
            return CandidateProfile()

    async def get_profile_dict(self, user_id: str) -> dict:
        profile = await self.get_candidate_profile(user_id)
        return {
            "name": profile.name_hint,
            "email": profile.email_hint,
            "total_years_experience": profile.total_years_experience,
            "current_role": profile.current_role,
            "current_company": profile.current_company,
            "is_embedded_engineer": profile.is_embedded_engineer,
            "embedded_domain_score": profile.embedded_domain_score,
            "skills": {
                "programming": profile.programming_languages,
                "rtos_os": profile.rtos_and_os,
                "protocols": profile.protocols,
                "hardware": profile.hardware_platforms,
                "automotive_safety": profile.automotive_safety,
                "tools": profile.tools_and_debug,
                "concepts": profile.software_concepts,
                "all": profile.all_skills,
                "count": profile.skill_count,
            },
            "education": {
                "degree": profile.highest_degree,
                "field": profile.field_of_study,
                "year": profile.graduation_year,
            },
            "profile_completeness": self._completeness(profile),
        }

    def _completeness(self, p: CandidateProfile) -> int:
        score = 0
        if p.name_hint: score += 15
        if p.email_hint: score += 10
        if p.total_years_experience > 0: score += 20
        if p.skill_count >= 5: score += 25
        if p.highest_degree: score += 15
        if p.is_embedded_engineer: score += 15
        return min(100, score)
