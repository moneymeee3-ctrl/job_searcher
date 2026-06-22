"""EMBEDHUNT AI — Company Service"""
from app.company.intelligence import REGISTRY, JOB_PORTALS, EMBEDDED_JOB_TITLES, CompanyTier, get_ordered_companies

class CompanyService:
    def get_intelligence_report(self) -> dict:
        ordered = get_ordered_companies()
        by_tier = {}
        for c in ordered:
            by_tier.setdefault(c.tier.value, []).append({"name": c.name, "careers_url": c.careers_url, "priority": c.priority})
        portals = sorted(JOB_PORTALS, key=lambda p: p["priority"], reverse=True)
        return {
            "total_companies": len(REGISTRY),
            "total_portals": len(JOB_PORTALS),
            "job_titles_monitored": EMBEDDED_JOB_TITLES,
            "salary_filter_lpa": 15.0,
            "companies_by_tier": by_tier,
            "portals_by_priority": portals,
            "scan_strategy": {
                "tier1": "Every 30 minutes",
                "tier2": "Every 2 hours",
                "tier3_plus": "Every 4 hours",
                "portals": "Every 15 minutes",
            }
        }

    def get_company_fit(self, company_name: str, matched_skills: list[str], match_score: int) -> dict:
        company = next((c for c in REGISTRY if c.name.lower() == company_name.lower()), None)
        if not company:
            return {"message": f"Company '{company_name}' not in intelligence database"}
        tier_difficulty = {
            CompanyTier.TIER1_SEMICONDUCTOR: {"difficulty": "Very High", "rounds": "5-8", "typical_salary_lpa": "25-50"},
            CompanyTier.TIER2_AUTOMOTIVE: {"difficulty": "High", "rounds": "4-6", "typical_salary_lpa": "15-30"},
            CompanyTier.TIER3_INDUSTRIAL: {"difficulty": "Medium", "rounds": "3-5", "typical_salary_lpa": "12-25"},
            CompanyTier.INDIA_FOCUSED: {"difficulty": "Medium", "rounds": "3-5", "typical_salary_lpa": "10-22"},
        }
        info = tier_difficulty.get(company.tier, {"difficulty": "Medium", "rounds": "3-5", "typical_salary_lpa": "10-20"})
        return {
            "company": company.name, "tier": company.tier.value,
            "careers_url": company.careers_url, "priority_rank": company.priority,
            "interview_difficulty": info["difficulty"],
            "typical_rounds": info["rounds"],
            "typical_salary_lpa": info["typical_salary_lpa"],
            "your_fit_score": match_score,
            "your_matched_skills": matched_skills,
            "preparation_tip": f"Focus on {company.tier.value.replace('_',' ')} domain knowledge and {matched_skills[0] if matched_skills else 'core embedded skills'}.",
        }
