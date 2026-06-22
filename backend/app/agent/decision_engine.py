"""EMBEDHUNT AI — Agent Decision Engine.

Given a ranked job and the candidate, decide the single best autonomous action.
Rules are deterministic and explainable (no black-box model) so the agent's
behaviour is auditable and reproducible — the standard a technical user expects.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from app.recommendation.explain import GapPriority
from app.recommendation.ranking import RankedJob


class AgentAction(str, Enum):
    APPLY_NOW = "apply_now"          # auto-apply candidate; act immediately
    RECOMMEND = "recommend"          # strong fit; surface to user to apply
    INTERVIEW_PREP = "interview_prep"  # strong fit but needs prep before applying
    UPSKILL_FIRST = "upskill_first"  # promising but blocked by critical gaps
    STRETCH = "stretch"              # aspirational; worth a roadmap, not a now-apply
    SKIP = "skip"                    # not worth pursuing


@dataclass
class Decision:
    job_id: str
    title: str
    company: str
    company_tier: str
    match_score: int
    meets_salary: bool
    action: AgentAction
    confidence: float                # 0.0 - 1.0
    rationale: str
    critical_gaps: list[str] = field(default_factory=list)
    next_artifact: str = ""          # which artifact the agent should produce: roadmap|interview_kit|none

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "title": self.title,
            "company": self.company,
            "company_tier": self.company_tier,
            "match_score": self.match_score,
            "meets_salary": self.meets_salary,
            "action": self.action.value,
            "confidence": round(self.confidence, 2),
            "rationale": self.rationale,
            "critical_gaps": self.critical_gaps,
            "next_artifact": self.next_artifact,
        }


def _critical_gaps(job: RankedJob) -> list[str]:
    return [g.skill for g in job.gap.high]


def _confidence(score: int, n_critical: int, meets_salary: bool) -> float:
    base = min(1.0, score / 99)
    base -= 0.06 * n_critical
    if not meets_salary:
        base -= 0.1
    return max(0.05, round(base, 3))


def decide_for_job(job: RankedJob) -> Decision:
    """Map a single ranked job to one explainable autonomous action."""
    score = job.match_score
    critical = _critical_gaps(job)
    n_crit = len(critical)
    conf = _confidence(score, n_crit, job.meets_salary)

    if job.is_auto_apply:
        action = AgentAction.APPLY_NOW
        artifact = "interview_kit"
        rationale = (
            f"Score {score}/99 with salary met and no blocking critical gaps — "
            f"top-tier fit. Apply now and prepare for interview."
        )
    elif score >= 70 and n_crit == 0:
        action = AgentAction.RECOMMEND
        artifact = "interview_kit"
        rationale = f"Strong fit (score {score}/99) with no critical gaps. Recommend applying."
    elif score >= 70:
        action = AgentAction.INTERVIEW_PREP
        artifact = "interview_kit"
        rationale = (
            f"Strong fit (score {score}/99) but {n_crit} critical gap(s): "
            f"{', '.join(critical[:3])}. Prep these, then apply."
        )
    elif score >= 55 and n_crit <= 2:
        action = AgentAction.RECOMMEND if n_crit == 0 else AgentAction.UPSKILL_FIRST
        artifact = "roadmap" if n_crit else "interview_kit"
        rationale = (
            f"Good fit (score {score}/99) with {n_crit} critical gap(s). "
            f"{'Close gaps then apply.' if n_crit else 'Worth applying.'}"
        )
    elif score >= 40:
        # Aspirational: better tier or higher pay justifies investing in a roadmap.
        action = AgentAction.STRETCH
        artifact = "roadmap"
        rationale = (
            f"Stretch role (score {score}/99). Critical gaps: {', '.join(critical[:3]) or 'none'}. "
            f"Build a roadmap before pursuing."
        )
    else:
        action = AgentAction.SKIP
        artifact = "none"
        rationale = f"Low overlap (score {score}/99). Not worth pursuing now."

    return Decision(
        job_id=job.job_id,
        title=job.title,
        company=job.company,
        company_tier=job.company_tier,
        match_score=score,
        meets_salary=job.meets_salary,
        action=action,
        confidence=conf,
        rationale=rationale,
        critical_gaps=critical,
        next_artifact=artifact,
    )


def decide_all(jobs: list[RankedJob]) -> list[Decision]:
    """Decide actions for every ranked job, preserving ranking order."""
    return [decide_for_job(j) for j in jobs]
