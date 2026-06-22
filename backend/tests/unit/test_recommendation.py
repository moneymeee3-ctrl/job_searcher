"""Unit tests — Recommendation, Gap, Ranking engines"""
import pytest
from app.resume.normalizer import CandidateProfile
from app.recommendation.matcher import compute_match
from app.recommendation.explain import analyze_gaps
from app.recommendation.ranking import rank_jobs, _meets_salary
from app.recommendation.engine import _job_corpus

STRONG = CandidateProfile(
    name_hint="Ram", total_years_experience=2.5, is_embedded_engineer=True,
    programming_languages=["c","c++","python"],
    rtos_and_os=["freertos","autosar"],
    protocols=["can","lin","spi","i2c","uart"],
    hardware_platforms=["arm","cortex-m","stm32"],
    automotive_safety=["iso 26262","asil","asil-b"],
    tools_and_debug=["jtag","gdb","jenkins","git"],
    software_concepts=["device driver","bsp","bare metal"],
    all_skills=["c","c++","python","freertos","autosar","can","lin","spi","i2c","uart",
                "arm","cortex-m","stm32","iso 26262","asil","asil-b","jtag","gdb","jenkins","device driver","bsp","bare metal"],
    skill_count=22, embedded_domain_score=75,
)

WEAK = CandidateProfile(
    all_skills=["python","git"], programming_languages=["python"], skill_count=2,
    is_embedded_engineer=False, embedded_domain_score=5, total_years_experience=1.0,
    rtos_and_os=[], protocols=[], hardware_platforms=[], automotive_safety=[], tools_and_debug=["git"], software_concepts=[],
)

Q_JOB = {"id":"q-001","title":"Senior Embedded SW Engineer","company":"Qualcomm","company_tier":"tier1_semiconductor","location":"Hyderabad","source_portal":"qualcomm_careers","source_url":"https://careers.qualcomm.com","apply_url":"https://careers.qualcomm.com","description":"ARM Cortex-M firmware RTOS C/C++ device drivers CAN ISO 26262","required_skills":"C,C++,ARM,RTOS,CAN,device driver,ISO 26262","experience_min":2,"salary_min_lpa":25.0,"salary_max_lpa":45.0}

class TestMatchingEngine:
    def test_strong_profile_scores_high(self):
        m = compute_match(STRONG, Q_JOB["title"], Q_JOB["description"], Q_JOB["required_skills"], Q_JOB["experience_min"])
        assert m.total_score >= 65

    def test_weak_profile_scores_low(self):
        m = compute_match(WEAK, Q_JOB["title"], Q_JOB["description"], Q_JOB["required_skills"])
        assert m.total_score < 40

    def test_score_bounded(self):
        m = compute_match(STRONG, Q_JOB["title"], Q_JOB["description"], Q_JOB["required_skills"])
        assert 0 <= m.total_score <= 99

    def test_category_scores_sum_to_base(self):
        m = compute_match(STRONG, Q_JOB["title"], Q_JOB["description"], Q_JOB["required_skills"])
        assert abs(sum(c.weighted_score for c in m.category_scores) - m.base_score) < 0.1

    def test_matched_in_profile(self):
        m = compute_match(STRONG, Q_JOB["title"], Q_JOB["description"], Q_JOB["required_skills"])
        pset = set(STRONG.all_skills)
        assert all(s in pset for s in m.matched_skills)

    def test_missing_not_in_profile(self):
        m = compute_match(STRONG, Q_JOB["title"], Q_JOB["description"], Q_JOB["required_skills"])
        pset = set(STRONG.all_skills)
        assert all(s not in pset for s in m.missing_skills)

    def test_explanation_present(self):
        m = compute_match(STRONG, Q_JOB["title"], Q_JOB["description"], Q_JOB["required_skills"])
        assert len(m.explanation) > 10

    def test_experience_bonus_applied(self):
        m = compute_match(STRONG, "Firmware Eng", None, "C,RTOS", exp_min=2)
        assert m.experience_bonus > 0

    def test_domain_bonus_for_embedded(self):
        m = compute_match(STRONG, "Automotive Firmware", "embedded automotive AUTOSAR firmware ECU", "C,AUTOSAR")
        assert m.domain_bonus > 0

    def test_no_domain_bonus_for_weak(self):
        m = compute_match(WEAK, "Automotive Firmware", "embedded automotive AUTOSAR firmware ECU", "C,AUTOSAR")
        assert m.domain_bonus == 0

class TestGapDetector:
    def _gap(self):
        m = compute_match(STRONG, Q_JOB["title"], Q_JOB["description"], Q_JOB["required_skills"])
        return analyze_gaps(m, Q_JOB["title"])

    def test_gaps_not_in_profile(self):
        gap = self._gap()
        pset = set(STRONG.all_skills)
        assert all(g.skill not in pset for g in gap.all_gaps)

    def test_resources_present(self):
        gap = self._gap()
        for g in gap.all_gaps: assert len(g.learning_resources) > 0

    def test_immediate_focus_max_3(self):
        gap = self._gap()
        assert len(gap.immediate_focus) <= 3

    def test_summary_present(self):
        gap = self._gap()
        assert len(gap.summary) > 10

class TestRankingEngine:
    def test_qualcomm_first(self):
        result = rank_jobs(STRONG, [Q_JOB], salary_min=15.0)
        if result.jobs: assert result.jobs[0].company == "Qualcomm"

    def test_ranks_sequential(self):
        result = rank_jobs(STRONG, [Q_JOB], salary_min=15.0)
        for i, j in enumerate(result.jobs, 1): assert j.rank == i

    def test_salary_filter(self):
        assert _meets_salary(25.0, 45.0, 15.0) is True
        assert _meets_salary(5.0, 9.0, 15.0) is False
        assert _meets_salary(None, None, 15.0) is True

    def test_total_scanned_correct(self):
        result = rank_jobs(STRONG, [Q_JOB])
        assert result.total_scanned == 1

    def test_full_corpus_runs(self):
        corpus = _job_corpus()
        result = rank_jobs(STRONG, corpus, min_score=40, salary_min=15.0)
        assert result.total_scanned == len(corpus)
        assert result.total_qualified <= result.total_scanned

class TestRoadmap:
    def test_roadmap_generated(self):
        from app.roadmap.planner import generate_roadmap
        r = generate_roadmap("uid", ["freertos","yocto"], 65, "Firmware Engineer")
        assert r.total_hours > 0 and len(r.tasks) == 2

    def test_immediate_actions_max_3(self):
        from app.roadmap.planner import generate_roadmap
        r = generate_roadmap("uid", ["freertos","yocto","bsp","can","lin"], 50, "Test")
        assert len(r.immediate_actions) <= 3

class TestInterviewKit:
    def test_kit_generated(self):
        from app.interview.generator import generate_interview_kit
        kit = generate_interview_kit("Embedded SW Engineer", "Qualcomm", ["c","rtos","can"], 75)
        assert kit.total_questions > 0 and kit.readiness_score > 0

    def test_questions_for_known_skills(self):
        from app.interview.question_bank import get_questions_for_skills
        qs = get_questions_for_skills(["c","rtos"])
        assert "c" in qs and "rtos" in qs

class TestCompanyIntelligence:
    def test_registry_count(self):
        from app.company.intelligence import REGISTRY
        assert len(REGISTRY) >= 50

    def test_qualcomm_highest_priority(self):
        from app.company.intelligence import get_ordered_companies
        assert get_ordered_companies()[0].name == "Qualcomm"

    def test_portals_count(self):
        from app.company.intelligence import JOB_PORTALS
        assert len(JOB_PORTALS) >= 10

class TestDashboardMetrics:
    def test_empty_state(self):
        from app.dashboard.metrics import compute_metrics
        m = compute_metrics([], 60, [])
        assert m.total_applications == 0 and m.conversion_rate == 0.0
