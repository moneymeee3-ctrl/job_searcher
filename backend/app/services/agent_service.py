"""EMBEDHUNT AI — Agent Service.

Database/IO glue for the autonomous career copilot. Loads the candidate profile,
runs the pure agent core and serialises the report for the API. Optionally queues
the agent's apply-now decisions as real applications (respecting the existing
application state machine via ``RecommendationService``).
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.decision_engine import AgentAction
from app.agent.executor import CareerCopilotAgent
from app.config.logging import get_logger
from app.services.profile_service import ProfileService
from app.services.recommendation_service import RecommendationService

logger = get_logger(__name__)


class AgentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.profile_svc = ProfileService(db)

    async def advise(
        self,
        user_id: str,
        *,
        min_score: int = 40,
        salary_min: float = 15.0,
    ) -> dict:
        """Run the copilot and return a full advisory report (no side effects)."""
        profile = await self.profile_svc.get_candidate_profile(user_id)
        report = CareerCopilotAgent(user_id=user_id).run(
            profile, min_score=min_score, salary_min=salary_min
        )
        logger.info(
            "agent_advise",
            user_id=user_id,
            readiness=report.insights.readiness_score,
            apply_now=len(report.scan.apply_now),
            steps=len(report.plan.steps),
        )
        return report.to_dict()

    async def auto_apply(
        self,
        user_id: str,
        *,
        salary_min: float = 15.0,
        max_applications: int = 5,
    ) -> dict:
        """Autonomously queue applications for the agent's apply-now decisions.

        Each application goes through ``RecommendationService.approve_apply`` so
        the existing application state machine and persistence are respected.
        """
        profile = await self.profile_svc.get_candidate_profile(user_id)
        report = CareerCopilotAgent(user_id=user_id).run(
            profile, salary_min=salary_min, build_artifacts=False
        )
        targets = [
            d for d in report.decisions if d.action == AgentAction.APPLY_NOW
        ][:max_applications]

        rec_svc = RecommendationService(self.db)
        queued: list[dict] = []
        skipped: list[dict] = []
        for decision in targets:
            try:
                app = await rec_svc.approve_apply(user_id, decision.job_id)
                queued.append({
                    "application_id": app.id,
                    "job": app.job_title,
                    "company": app.company_name,
                    "match_score": app.match_score,
                    "status": app.status.value,
                })
            except Exception as exc:  # noqa: BLE001 — surface per-job failure, keep going
                logger.warning("auto_apply_skip", job_id=decision.job_id, error=str(exc))
                skipped.append({"job_id": decision.job_id, "reason": str(exc)})

        logger.info("agent_auto_apply", user_id=user_id, queued=len(queued), skipped=len(skipped))
        return {
            "queued_count": len(queued),
            "skipped_count": len(skipped),
            "queued": queued,
            "skipped": skipped,
            "summary": (
                f"Autonomously queued {len(queued)} application(s) from "
                f"{len(report.scan.apply_now)} apply-now match(es)."
            ),
        }
