"""EMBEDHUNT AI — Dashboard Metrics Calculator"""
from dataclasses import dataclass, field

@dataclass
class DashboardMetrics:
    profile_score: int = 0
    total_applications: int = 0
    pending_applications: int = 0
    submitted_applications: int = 0
    interviews_scheduled: int = 0
    offers_received: int = 0
    rejections: int = 0
    conversion_rate: float = 0.0
    interview_rate: float = 0.0
    offer_rate: float = 0.0
    avg_match_score: float = 0.0
    top_companies_applied: list[str] = field(default_factory=list)
    skills_count: int = 0
    embedded_domain_score: int = 0
    recommendations_available: int = 0
    auto_apply_ready: int = 0

def compute_metrics(applications: list, profile_score: int, recommendations: list) -> DashboardMetrics:
    total = len(applications)
    submitted = sum(1 for a in applications if a.status.value in ("submitted","responded"))
    interviews = sum(1 for a in applications if a.outcome.value == "interview")
    offers = sum(1 for a in applications if a.outcome.value == "offer")
    rejections = sum(1 for a in applications if a.outcome.value == "rejected")
    avg_score = round(sum(a.match_score for a in applications) / total, 1) if total else 0.0
    conversion = round(submitted / total * 100, 1) if total else 0.0
    interview_rate = round(interviews / submitted * 100, 1) if submitted else 0.0
    offer_rate = round(offers / interviews * 100, 1) if interviews else 0.0
    top_cos = list(dict.fromkeys(a.company_name for a in sorted(applications, key=lambda x: x.match_score, reverse=True)))[:5]
    auto_ready = sum(1 for r in recommendations if r.get("is_auto_apply"))
    return DashboardMetrics(
        profile_score=profile_score, total_applications=total,
        pending_applications=total - submitted, submitted_applications=submitted,
        interviews_scheduled=interviews, offers_received=offers,
        rejections=rejections, conversion_rate=conversion,
        interview_rate=interview_rate, offer_rate=offer_rate,
        avg_match_score=avg_score, top_companies_applied=top_cos,
        recommendations_available=len(recommendations), auto_apply_ready=auto_ready,
    )
