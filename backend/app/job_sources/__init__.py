"""EMBEDHUNT AI — Job Discovery subsystem.

Legitimate, agentic job discovery over public ATS/job APIs (Greenhouse, Lever,
RemoteOK). Produces recommendation-engine corpus dicts so discovered jobs flow
straight into ranking and the autonomous agent pipeline.
"""
from app.job_sources.aggregator import DiscoveryResult, discover
from app.job_sources.base import Fetcher, JobSource, JobSourceError, http_json_fetcher
from app.job_sources.greenhouse import GreenhouseSource
from app.job_sources.lever import LeverSource
from app.job_sources.registry import default_sources
from app.job_sources.remoteok import RemoteOkSource
from app.job_sources.schema import JobPosting

__all__ = [
    "DiscoveryResult",
    "discover",
    "Fetcher",
    "JobSource",
    "JobSourceError",
    "http_json_fetcher",
    "GreenhouseSource",
    "LeverSource",
    "RemoteOkSource",
    "default_sources",
    "JobPosting",
]
