"""EMBEDHUNT AI — Greenhouse connector.

Consumes the **public** Greenhouse Boards API that companies embed on their own
career sites:

    https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true

Thousands of tech companies and startups host their listings here, making this a
high-quality Priority-1/Priority-2 source.
"""
from __future__ import annotations

from app.job_sources.base import Fetcher, JobSource
from app.job_sources.schema import JobPosting

_API = "https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"


class GreenhouseSource(JobSource):
    def __init__(self, board_token: str, company: str, company_tier: str = "other") -> None:
        self.board_token = board_token
        self.company = company
        self.company_tier = company_tier
        self.name = f"greenhouse:{board_token}"

    def fetch(self, fetcher: Fetcher) -> list[JobPosting]:
        data = fetcher(_API.format(board=self.board_token))
        raw_jobs = data.get("jobs", []) if isinstance(data, dict) else []
        postings: list[JobPosting] = []
        for job in raw_jobs:
            location = ""
            loc = job.get("location")
            if isinstance(loc, dict):
                location = loc.get("name", "")
            apply_url = job.get("absolute_url", "")
            postings.append(
                JobPosting(
                    external_id=str(job.get("id", "")),
                    title=job.get("title", ""),
                    company=self.company,
                    location=location,
                    apply_url=apply_url,
                    description=job.get("content", ""),
                    source_portal=self.name,
                    source_url=apply_url,
                    company_tier=self.company_tier,
                )
            )
        return postings
