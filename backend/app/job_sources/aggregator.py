"""EMBEDHUNT AI — Discovery aggregator.

Fans out across all configured sources, isolates per-source failures (one dead
ATS never breaks discovery), filters to in-scope roles, de-duplicates, and emits
recommendation-engine corpus dicts. This is the seam the agent's
``opportunity_finder`` is designed to plug into.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from app.job_sources.base import Fetcher, JobSource, JobSourceError, http_json_fetcher
from app.job_sources.registry import default_sources
from app.job_sources.schema import JobPosting

logger = logging.getLogger("embedhunt.discovery")


@dataclass
class DiscoveryResult:
    postings: list[JobPosting] = field(default_factory=list)
    sources_ok: list[str] = field(default_factory=list)
    sources_failed: list[str] = field(default_factory=list)

    def to_corpus(self) -> list[dict]:
        return [p.to_corpus_dict() for p in self.postings]


def discover(
    *,
    sources: list[JobSource] | None = None,
    fetcher: Fetcher | None = None,
    limit_per_source: int = 100,
) -> DiscoveryResult:
    """Run discovery across ``sources`` and return relevant, de-duplicated jobs."""
    sources = sources if sources is not None else default_sources()
    fetcher = fetcher or http_json_fetcher

    result = DiscoveryResult()
    seen: set[str] = set()

    for source in sources:
        try:
            postings = source.fetch(fetcher)
        except JobSourceError as exc:
            logger.warning("discovery source failed: %s (%s)", source.name, exc)
            result.sources_failed.append(source.name)
            continue
        except Exception as exc:  # noqa: BLE001 — never let one source kill discovery
            logger.warning("discovery source errored: %s (%s)", source.name, exc)
            result.sources_failed.append(source.name)
            continue

        result.sources_ok.append(source.name)
        kept = 0
        for posting in postings:
            if kept >= limit_per_source:
                break
            if not posting.title or not posting.is_relevant():
                continue
            key = posting.dedup_key
            if key in seen:
                continue
            seen.add(key)
            result.postings.append(posting)
            kept += 1

    return result
