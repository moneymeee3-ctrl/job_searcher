"""EMBEDHUNT AI — Job Discovery: source abstraction + HTTP fetcher.

Connectors only consume **legitimate public JSON endpoints** that companies
intentionally expose to render their own career pages (Greenhouse, Lever) or that
publish an official public API (RemoteOK). No site that prohibits automated
access is scraped.

HTTP is abstracted behind the :data:`Fetcher` callable so the whole subsystem is
unit-testable without network access — tests inject a fixture fetcher. The
default fetcher uses the standard library only (no third-party dependency), so
discovery works on a bare interpreter.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from typing import Any, Callable

from app.job_sources.schema import JobPosting

# A Fetcher takes a URL and returns parsed JSON (dict or list).
Fetcher = Callable[[str], Any]

_DEFAULT_TIMEOUT = 12
_USER_AGENT = "EmbedhuntAI-JobDiscovery/1.0 (+https://embedhunt.ai)"


class JobSourceError(RuntimeError):
    """Raised when a source cannot be fetched or parsed."""


def http_json_fetcher(url: str, *, timeout: int = _DEFAULT_TIMEOUT) -> Any:
    """Default fetcher: GET ``url`` and parse JSON using only the stdlib."""
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 (https only, see guard)
            if not url.lower().startswith("https://"):
                raise JobSourceError(f"Refusing non-HTTPS URL: {url}")
            payload = response.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
        raise JobSourceError(f"Fetch failed for {url}: {exc}") from exc
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise JobSourceError(f"Invalid JSON from {url}: {exc}") from exc


class JobSource(ABC):
    """A discoverable source of job postings."""

    #: Stable, human-readable identifier, e.g. ``"greenhouse:nvidia"``.
    name: str

    @abstractmethod
    def fetch(self, fetcher: Fetcher) -> list[JobPosting]:
        """Return normalized postings, using ``fetcher`` for all HTTP I/O."""
        raise NotImplementedError
