"""EMBEDHUNT AI — Lever connector.

Consumes the **public** Lever postings API used to render companies' own career
pages:

    https://api.lever.co/v0/postings/{company}?mode=json

Widely used by startups and scale-ups — a strong Priority-2 source.
"""
from __future__ import annotations

from app.job_sources.base import Fetcher, JobSource
from app.job_sources.schema import JobPosting

_API = "https://api.lever.co/v0/postings/{company}?mode=json"


class LeverSource(JobSource):
    def __init__(self, company_slug: str, company: str, company_tier: str = "other") -> None:
        self.company_slug = company_slug
        self.company = company
        self.company_tier = company_tier
        self.name = f"lever:{company_slug}"

    def fetch(self, fetcher: Fetcher) -> list[JobPosting]:
        data = fetcher(_API.format(company=self.company_slug))
        raw_jobs = data if isinstance(data, list) else []
        postings: list[JobPosting] = []
        for job in raw_jobs:
            categories = job.get("categories", {}) or {}
            location = categories.get("location", "")
            description = job.get("descriptionPlain") or job.get("description", "")
            apply_url = job.get("hostedUrl") or job.get("applyUrl", "")
            postings.append(
                JobPosting(
                    external_id=str(job.get("id", "")),
                    title=job.get("text", ""),
                    company=self.company,
                    location=location,
                    apply_url=apply_url,
                    description=description,
                    source_portal=self.name,
                    source_url=apply_url,
                    company_tier=self.company_tier,
                )
            )
        return postings
