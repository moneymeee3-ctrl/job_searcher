"""EMBEDHUNT AI — Naukri connector (opt-in).

Consumes a Naukri-style JSON search response. Naukri does NOT expose a general
public discovery API and its Terms of Service restrict automated access, so this
connector is intentionally **not** part of the default source set: it is only
usable with a legitimate/partner feed URL supplied by the operator. HTTP remains
abstracted behind ``fetcher`` for testability.
"""
from __future__ import annotations

from app.job_sources.base import Fetcher, JobSource
from app.job_sources.schema import JobPosting


class NaukriSource(JobSource):
    def __init__(self, feed_url: str, company_tier: str = "india_focused") -> None:
        self.feed_url = feed_url
        self.company_tier = company_tier
        self.name = "naukri"

    def fetch(self, fetcher: Fetcher) -> list[JobPosting]:
        data = fetcher(self.feed_url)
        rows = data.get("jobDetails", []) if isinstance(data, dict) else []
        postings: list[JobPosting] = []
        for job in rows:
            ext_id = str(job.get("jobId", "") or job.get("jdURL", ""))
            skills = job.get("tagsAndSkills", "") or ""
            required = [s.strip().lower() for s in skills.split(",") if s.strip()]
            exp_min = None
            exp = job.get("experienceText") or ""
            digits = "".join(c if c.isdigit() else " " for c in exp).split()
            if digits:
                exp_min = int(digits[0])
            postings.append(
                JobPosting(
                    external_id=ext_id,
                    title=job.get("title", "") or job.get("designation", ""),
                    company=job.get("companyName", ""),
                    location=job.get("placeholders", {}).get("location", "")
                    if isinstance(job.get("placeholders"), dict) else job.get("location", ""),
                    apply_url=job.get("jdURL", ""),
                    description=job.get("jobDescription", "") or job.get("title", ""),
                    source_portal=self.name,
                    source_url=job.get("jdURL", ""),
                    company_tier=self.company_tier,
                    experience_min=exp_min,
                    required_skills=required,
                )
            )
        return postings
