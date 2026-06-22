"""EMBEDHUNT AI — Dashboard Service"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.profile_service import ProfileService
from app.services.recommendation_service import RecommendationService
from app.repositories.application_repository import ApplicationRepository
from app.dashboard.metrics import compute_metrics

class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard(self, user_id: str) -> dict:
        profile_svc = ProfileService(self.db)
        profile_dict = await profile_svc.get_profile_dict(user_id)
        rec_svc = RecommendationService(self.db)
        rec_data = await rec_svc.get_recommendations(user_id, min_score=40, salary_min=15.0)
        app_repo = ApplicationRepository(self.db)
        applications = await app_repo.get_by_user(user_id)
        metrics = compute_metrics(applications, profile_dict["profile_completeness"], rec_data.get("jobs", []))
        return {
            "profile": profile_dict,
            "metrics": {
                "profile_score": metrics.profile_score,
                "total_applications": metrics.total_applications,
                "submitted": metrics.submitted_applications,
                "interviews": metrics.interviews_scheduled,
                "offers": metrics.offers_received,
                "conversion_rate": metrics.conversion_rate,
                "interview_rate": metrics.interview_rate,
                "offer_rate": metrics.offer_rate,
                "avg_match_score": metrics.avg_match_score,
            },
            "recommendations_summary": {
                "total_qualified": rec_data.get("total_qualified", 0),
                "auto_apply_ready": rec_data.get("auto_apply_count", 0),
                "strong_matches": rec_data.get("strong_count", 0),
                "top_5": rec_data.get("jobs", [])[:5],
            },
            "recent_applications": [
                {"job": a.job_title, "company": a.company_name, "score": a.match_score,
                 "status": a.status.value, "outcome": a.outcome.value}
                for a in applications[:5]
            ],
            "intelligence": {
                "companies_monitored": 55,
                "portals_monitored": 13,
                "job_titles_tracked": 19,
                "salary_filter": "≥15 LPA",
            }
        }
