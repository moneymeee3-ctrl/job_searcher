"""EMBEDHUNT AI — Agentic Career Copilot.

This package contains the autonomous reasoning core of EMBEDHUNT AI. It is
deliberately pure (no database, no network, no FastAPI) so it can be reasoned
about and unit-tested deterministically. All I/O glue lives in the service
layer (``app.services.agent_service``).

Pipeline:
    observe (reasoner)  ->  find opportunities (opportunity_finder)
        ->  decide per-opportunity (decision_engine)
        ->  plan (planner)  ->  coach (career_coach)
        ->  execute / produce artifacts (executor)

The orchestrator (``CareerCopilotAgent``) wires these stages together and
records every step in an ``AgentMemory`` trace for explainability.
"""
from app.agent.memory import AgentMemory, MemoryEntry
from app.agent.decision_engine import AgentAction, Decision, decide_for_job, decide_all
from app.agent.reasoner import CareerInsights, reason_about_career
from app.agent.opportunity_finder import Opportunity, OpportunityScan, find_opportunities
from app.agent.planner import ActionPlan, PlannedStep, StepKind, build_plan
from app.agent.career_coach import CoachingBrief, coach
from app.agent.executor import AgentReport, CareerCopilotAgent

__all__ = [
    "AgentMemory", "MemoryEntry",
    "AgentAction", "Decision", "decide_for_job", "decide_all",
    "CareerInsights", "reason_about_career",
    "Opportunity", "OpportunityScan", "find_opportunities",
    "ActionPlan", "PlannedStep", "StepKind", "build_plan",
    "CoachingBrief", "coach",
    "AgentReport", "CareerCopilotAgent",
]
