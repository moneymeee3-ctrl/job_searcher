"""Unit tests — Autonomous Agent core (reasoner, decision engine, planner, coach, orchestrator)."""
import pytest

from app.agent import (
    AgentAction,
    CareerCopilotAgent,
    build_plan,
    coach,
    decide_all,
    find_opportunities,
    reason_about_career,
)
from app.agent.planner import StepKind
from app.recommendation.engine import run_matching
from app.resume.normalizer import CandidateProfile

STRONG = CandidateProfile(
    name_hint="Ram", total_years_experience=4.0, is_embedded_engineer=True,
    programming_languages=["c", "c++", "python"],
    rtos_and_os=["freertos", "autosar"],
    protocols=["can", "lin", "spi", "i2c", "uart", "ethernet"],
    hardware_platforms=["arm", "cortex-m", "stm32"],
    automotive_safety=["iso 26262", "asil", "misra c"],
    tools_and_debug=["jtag", "gdb", "git"],
    software_concepts=["device driver", "bsp", "bare metal", "bootloader"],
    all_skills=["c", "c++", "python", "freertos", "autosar", "can", "lin", "spi", "i2c",
                "uart", "ethernet", "arm", "cortex-m", "stm32", "iso 26262", "asil",
                "misra c", "jtag", "gdb", "git", "device driver", "bsp", "bare metal", "bootloader"],
    skill_count=24, embedded_domain_score=85,
)

WEAK = CandidateProfile(
    all_skills=["python", "git"], programming_languages=["python"], skill_count=2,
    is_embedded_engineer=False, embedded_domain_score=5, total_years_experience=1.0,
    rtos_and_os=[], protocols=[], hardware_platforms=[], automotive_safety=[],
    tools_and_debug=["git"], software_concepts=[],
)


@pytest.fixture
def strong_scan():
    result = run_matching(STRONG, min_score=40, salary_min=15.0)
    return find_opportunities(STRONG, result=result)


class TestOpportunityFinder:
    def test_buckets_partition_jobs(self, strong_scan):
        total = len(strong_scan.apply_now) + len(strong_scan.strong) + len(strong_scan.stretch)
        assert total == len(strong_scan.opportunities)

    def test_strong_profile_finds_opportunities(self, strong_scan):
        assert len(strong_scan.opportunities) > 0

    def test_apply_now_are_auto_apply(self, strong_scan):
        assert all(o.is_auto_apply for o in strong_scan.apply_now)

    def test_serializable(self, strong_scan):
        for o in strong_scan.opportunities:
            d = o.to_dict()
            assert d["bucket"] in ("apply_now", "strong", "stretch")


class TestReasoner:
    def test_strong_profile_high_readiness(self, strong_scan):
        insights = reason_about_career(STRONG, strong_scan.result)
        assert insights.readiness_score >= 55
        assert insights.readiness_level in ("competitive", "strong", "elite")

    def test_weak_profile_low_readiness(self):
        result = run_matching(WEAK, min_score=0, salary_min=0)
        insights = reason_about_career(WEAK, result)
        assert insights.readiness_score < 55
        assert insights.readiness_level in ("not_ready", "emerging")

    def test_top_skill_gaps_capped(self, strong_scan):
        insights = reason_about_career(STRONG, strong_scan.result)
        assert len(insights.top_skill_gaps) <= 8

    def test_headline_present(self, strong_scan):
        insights = reason_about_career(STRONG, strong_scan.result)
        assert len(insights.headline) > 10


class TestDecisionEngine:
    def test_one_decision_per_job(self, strong_scan):
        decisions = decide_all(strong_scan.result.jobs)
        assert len(decisions) == len(strong_scan.result.jobs)

    def test_auto_apply_jobs_become_apply_now(self, strong_scan):
        decisions = decide_all(strong_scan.result.jobs)
        for d in decisions:
            job = next(j for j in strong_scan.result.jobs if j.job_id == d.job_id)
            if job.is_auto_apply:
                assert d.action == AgentAction.APPLY_NOW

    def test_confidence_bounded(self, strong_scan):
        for d in decide_all(strong_scan.result.jobs):
            assert 0.0 <= d.confidence <= 1.0

    def test_actions_are_valid(self, strong_scan):
        for d in decide_all(strong_scan.result.jobs):
            assert d.action in set(AgentAction)


class TestPlanner:
    def test_orders_sequential(self, strong_scan):
        insights = reason_about_career(STRONG, strong_scan.result)
        decisions = decide_all(strong_scan.result.jobs)
        plan = build_plan(insights, decisions)
        for i, step in enumerate(plan.steps, 1):
            assert step.order == i

    def test_respects_max_steps(self, strong_scan):
        insights = reason_about_career(STRONG, strong_scan.result)
        decisions = decide_all(strong_scan.result.jobs)
        plan = build_plan(insights, decisions, max_steps=3)
        assert len(plan.steps) <= 3

    def test_weak_profile_gets_improve_profile_step(self):
        result = run_matching(WEAK, min_score=0, salary_min=0)
        insights = reason_about_career(WEAK, result)
        decisions = decide_all(result.jobs)
        plan = build_plan(insights, decisions)
        assert any(s.kind == StepKind.IMPROVE_PROFILE for s in plan.steps)

    def test_apply_steps_ranked_before_upskill(self, strong_scan):
        insights = reason_about_career(STRONG, strong_scan.result)
        decisions = decide_all(strong_scan.result.jobs)
        plan = build_plan(insights, decisions)
        kinds = [s.kind for s in plan.steps]
        if StepKind.APPLY in kinds and StepKind.UPSKILL in kinds:
            assert kinds.index(StepKind.APPLY) < kinds.index(StepKind.UPSKILL)


class TestCoach:
    def test_brief_has_actions(self, strong_scan):
        insights = reason_about_career(STRONG, strong_scan.result)
        decisions = decide_all(strong_scan.result.jobs)
        brief = coach(insights, strong_scan, decisions)
        assert len(brief.next_best_actions) > 0

    def test_interview_target_set_for_strong(self, strong_scan):
        insights = reason_about_career(STRONG, strong_scan.result)
        decisions = decide_all(strong_scan.result.jobs)
        brief = coach(insights, strong_scan, decisions)
        assert brief.interview_target_job_id is not None


class TestOrchestrator:
    def test_full_run_serializable(self):
        report = CareerCopilotAgent(user_id="u1").run(STRONG)
        d = report.to_dict()
        assert "insights" in d and "plan" in d and "coaching" in d and "trace" in d

    def test_strong_profile_produces_artifacts(self):
        report = CareerCopilotAgent(user_id="u1").run(STRONG)
        # A strong embedded profile should anchor at least an interview kit.
        assert report.interview_kit is not None

    def test_trace_records_all_phases(self):
        report = CareerCopilotAgent(user_id="u1").run(STRONG)
        phases = set(report.memory.phases())
        assert {"find", "reason", "decide", "plan", "coach"}.issubset(phases)

    def test_weak_profile_no_apply_now(self):
        report = CareerCopilotAgent(user_id="u2").run(WEAK, min_score=0, salary_min=0)
        assert len(report.scan.apply_now) == 0

    def test_empty_profile_warns(self):
        report = CareerCopilotAgent().run(CandidateProfile())
        assert any("resume" in w.lower() for w in report.warnings)

    def test_run_is_deterministic(self):
        a = CareerCopilotAgent(user_id="u1").run(STRONG).to_dict()
        b = CareerCopilotAgent(user_id="u1").run(STRONG).to_dict()
        assert a["plan"]["summary"] == b["plan"]["summary"]
        assert a["insights"]["readiness_score"] == b["insights"]["readiness_score"]
