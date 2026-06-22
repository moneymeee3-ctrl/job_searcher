"""EMBEDHUNT AI — Agent Executor & Orchestrator.

``CareerCopilotAgent`` runs the full autonomous pipeline and produces concrete
deliverables (a learning roadmap for the best near-miss role and an interview kit
for the best apply-ready role). The core stays side-effect-free: persistence and
real application submission are performed by the service layer, which consumes
this report.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.agent.career_coach import CoachingBrief, coach
from app.agent.decision_engine import Decision, decide_all
from app.agent.memory import AgentMemory
from app.agent.opportunity_finder import OpportunityScan, find_opportunities
from app.agent.planner import ActionPlan, build_plan
from app.agent.reasoner import CareerInsights, reason_about_career
from app.interview.generator import generate_interview_kit
from app.recommendation.ranking import RankedJob, RankingResult
from app.resume.normalizer import CandidateProfile
from app.roadmap.planner import LearningRoadmap, generate_roadmap


@dataclass
class AgentReport:
    insights: CareerInsights
    scan: OpportunityScan
    decisions: list[Decision]
    plan: ActionPlan
    coaching: CoachingBrief
    memory: AgentMemory
    roadmap: LearningRoadmap | None = None
    interview_kit: Any | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "insights": self.insights.to_dict(),
            "market_scan": {
                "summary": self.scan.result.summary,
                "total_scanned": self.scan.result.total_scanned,
                "total_qualified": self.scan.result.total_qualified,
                "apply_now": [o.to_dict() for o in self.scan.apply_now],
                "strong": [o.to_dict() for o in self.scan.strong],
                "stretch": [o.to_dict() for o in self.scan.stretch],
            },
            "decisions": [d.to_dict() for d in self.decisions],
            "plan": self.plan.to_dict(),
            "coaching": self.coaching.to_dict(),
            "roadmap": _serialize_roadmap(self.roadmap) if self.roadmap else None,
            "interview_kit": _serialize_kit(self.interview_kit) if self.interview_kit else None,
            "warnings": self.warnings,
            "trace": self.memory.to_dict(),
        }


def _serialize_roadmap(r: LearningRoadmap) -> dict:
    return {
        "job_title": r.job_title,
        "current_score": r.current_score,
        "projected_score": r.projected_score,
        "total_hours": r.total_hours,
        "total_weeks": r.total_weeks,
        "immediate_actions": r.immediate_actions,
        "summary": r.summary,
        "tasks": [
            {
                "skill": t.skill,
                "priority": t.priority,
                "estimated_hours": t.estimated_hours,
                "level": t.level.value,
                "weeks_estimate": t.weeks_estimate,
                "resources": t.resources,
            }
            for t in r.tasks
        ],
    }


def _serialize_kit(k: Any) -> dict:
    return {
        "job_title": k.job_title,
        "company": k.company,
        "readiness_score": k.readiness_score,
        "focus_skills": k.focus_skills,
        "coding_topics": k.coding_topics,
        "checklist": k.checklist,
        "total_questions": k.total_questions,
        "questions_by_skill": k.questions_by_skill,
        "preparation_summary": k.preparation_summary,
    }


class CareerCopilotAgent:
    """Autonomous career copilot: observe -> find -> decide -> plan -> coach -> execute."""

    def __init__(self, user_id: str = "anonymous"):
        self.user_id = user_id

    def _find_job(self, result: RankingResult, job_id: str | None) -> RankedJob | None:
        if not job_id:
            return None
        return next((j for j in result.jobs if j.job_id == job_id), None)

    def run(
        self,
        profile: CandidateProfile,
        *,
        min_score: int = 40,
        salary_min: float = 15.0,
        result: RankingResult | None = None,
        build_artifacts: bool = True,
        live: bool = False,
        fetcher=None,
    ) -> AgentReport:
        memory = AgentMemory()
        warnings: list[str] = []

        if profile.skill_count == 0:
            warnings.append("No parsed skills found — upload a resume for a full analysis.")

        # 0. Optionally discover live jobs across public ATS/job APIs and use them
        #    as the market to scan. Degrades gracefully to the seed corpus.
        if result is None and live:
            from app.recommendation.engine import run_live_matching

            result, discovery = run_live_matching(
                profile, min_score=min_score, salary_min=salary_min, fetcher=fetcher
            )
            memory.log("discover", "Discovered live opportunities",
                       sources_ok=discovery.sources_ok, sources_failed=discovery.sources_failed,
                       discovered=len(discovery.postings))
            if not discovery.sources_ok:
                warnings.append("Live discovery sources unavailable — used curated corpus.")

        # 1. Find opportunities (proactive scan).
        scan = find_opportunities(profile, min_score=min_score, salary_min=salary_min, result=result)
        memory.remember("ranking", scan.result)
        memory.log("find", "Scanned the market",
                    scanned=scan.result.total_scanned, qualified=scan.result.total_qualified,
                    apply_now=len(scan.apply_now), strong=len(scan.strong), stretch=len(scan.stretch))

        # 2. Reason about the career.
        insights = reason_about_career(profile, scan.result)
        memory.log("reason", insights.headline,
                   readiness=insights.readiness_score, level=insights.readiness_level)

        # 3. Decide per opportunity.
        decisions = decide_all(scan.result.jobs)
        memory.log("decide", "Decided an action for each opportunity",
                   decisions=_count_actions(decisions))

        # 4. Plan.
        plan = build_plan(insights, decisions)
        memory.log("plan", plan.summary, steps=len(plan.steps))

        # 5. Coach.
        brief = coach(insights, scan, decisions)
        memory.log("coach", brief.headline, actions=len(brief.next_best_actions))

        # 6. Execute — produce concrete artifacts.
        roadmap = None
        interview_kit = None
        if build_artifacts:
            roadmap_job = self._find_job(scan.result, brief.roadmap_target_job_id)
            if roadmap_job is not None:
                roadmap = generate_roadmap(
                    self.user_id,
                    roadmap_job.match.missing_skills,
                    roadmap_job.match_score,
                    roadmap_job.title,
                )
                memory.log("execute", "Generated learning roadmap",
                           target=roadmap_job.title, weeks=roadmap.total_weeks)

            kit_job = self._find_job(scan.result, brief.interview_target_job_id)
            if kit_job is not None:
                interview_kit = generate_interview_kit(
                    kit_job.title, kit_job.company,
                    kit_job.match.matched_skills, kit_job.match_score,
                )
                memory.log("execute", "Generated interview kit",
                           target=kit_job.title, readiness=interview_kit.readiness_score)

        return AgentReport(
            insights=insights,
            scan=scan,
            decisions=decisions,
            plan=plan,
            coaching=brief,
            memory=memory,
            roadmap=roadmap,
            interview_kit=interview_kit,
            warnings=warnings,
        )


def _count_actions(decisions: list[Decision]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for d in decisions:
        counts[d.action.value] = counts.get(d.action.value, 0) + 1
    return counts
