"""EMBEDHUNT AI — RemoteOK connector.

Consumes RemoteOK's **official public API** (https://remoteok.com/api). The first
element of the response is an attribution/legal notice object (not a job) and is
skipped. A Priority-4 (remote) source.
"""
from __future__ import annotations

from app.job_sources.base import Fetcher, JobSource
from app.job_sources.schema import JobPosting

_API = "https://remoteok.com/api"


class RemoteOkSource(JobSource):
    def __init__(self) -> None:
        self.name = "remoteok"

    def fetch(self, fetcher: Fetcher) -> list[JobPosting]:
        data = fetcher(_API)
        rows = data if isinstance(data, list) else []
        postings: list[JobPosting] = []
        for row in rows:
            # The leading legal-notice object has no "position"/"id" job fields.
            if not isinstance(row, dict) or "position" not in row:
                continue
            tags = row.get("tags") or []
            description = row.get("description", "")
            if tags:
                description = f"{description}. Skills: {', '.join(str(t) for t in tags)}"
            apply_url = row.get("url", "") or row.get("apply_url", "")
            postings.append(
                JobPosting(
                    external_id=str(row.get("id", "")),
                    title=row.get("position", ""),
                    company=row.get("company", ""),
                    location=row.get("location") or "Remote",
                    apply_url=apply_url,
                    description=description,
                    source_portal=self.name,
                    source_url=apply_url,
                    company_tier="remote",
                )
            )
        return postings
