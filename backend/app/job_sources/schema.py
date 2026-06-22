"""EMBEDHUNT AI — Job Discovery: normalized posting schema.

Every connector produces :class:`JobPosting` objects. ``to_corpus_dict`` maps a
posting into the exact dict shape the (already tested) recommendation engine
consumes (see ``app.recommendation.engine._job_corpus``), so discovered jobs flow
through ranking/agent code with zero downstream changes.
"""
from __future__ import annotations

import html
import re
from dataclasses import dataclass, field

from app.resume.extractor import extract_skills

# Title keywords that mark a posting as in-scope for EMBEDHUNT's audience.
# Deliberately broad (the product must not restrict itself to predefined roles)
# but specific enough to exclude clearly-unrelated postings (sales, HR, etc.).
_ROLE_KEYWORDS = (
    "embedded", "firmware", "software", "engineer", "developer", "linux",
    "kernel", "driver", "rtos", "bsp", "yocto", "platform", "system",
    "autosar", "automotive", "adas", "ecu", "middleware", "fpga", "asic",
    "verification", "validation", "robotics", "mechatronics", "dsp",
    "signal processing", "control systems", "compiler", "toolchain", "edge ai",
    "embedded ai", "machine learning", "ml ", "ai ", "mlops", "devops",
    "cloud", "backend", "c++", "c programmer", "python", "rust", "architect",
    "technical lead", "principal", "staff",
)

# Non-engineering roles to actively exclude even if a generic keyword matches.
_EXCLUDE_KEYWORDS = (
    "sales", "account executive", "recruiter", "human resources", " hr ",
    "marketing", "customer success", "accountant", "legal counsel",
    "administrative", "receptionist", "intern, marketing",
)

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
_YEARS_RE = re.compile(r"(\d{1,2})\s*\+?\s*(?:-\s*\d{1,2}\s*)?years?", re.IGNORECASE)


def strip_html(text: str | None) -> str:
    """Convert ATS HTML/escaped content into clean plain text."""
    if not text:
        return ""
    text = html.unescape(text)
    text = _TAG_RE.sub(" ", text)
    return _WS_RE.sub(" ", text).strip()


def parse_min_experience(text: str | None) -> int | None:
    """Best-effort minimum-years-of-experience extraction from free text."""
    if not text:
        return None
    matches = _YEARS_RE.findall(text)
    if not matches:
        return None
    try:
        # Smallest plausible "N years" mention is the most likely minimum.
        years = sorted(int(m) for m in matches if 0 <= int(m) <= 40)
    except ValueError:
        return None
    return years[0] if years else None


@dataclass
class JobPosting:
    """A single discovered job, normalized across all sources."""

    external_id: str
    title: str
    company: str
    location: str
    apply_url: str
    description: str
    source_portal: str               # e.g. "greenhouse:nvidia"
    source_url: str
    company_tier: str = "other"
    salary_min_lpa: float | None = None
    salary_max_lpa: float | None = None
    experience_min: int | None = None
    experience_max: int | None = None
    required_skills: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.title = (self.title or "").strip()
        self.company = (self.company or "").strip()
        self.location = (self.location or "").strip() or "Not specified"
        self.description = strip_html(self.description)
        if not self.required_skills:
            corpus = f"{self.title}. {self.description}"
            self.required_skills = extract_skills(corpus).all_skills
        if self.experience_min is None:
            self.experience_min = parse_min_experience(self.description)

    @property
    def dedup_key(self) -> str:
        return f"{self.company.lower()}::{self.title.lower()}"

    def is_relevant(self) -> bool:
        """Keep only engineering/software postings relevant to the audience."""
        haystack = f"{self.title} {self.location}".lower()
        if any(bad in haystack for bad in _EXCLUDE_KEYWORDS):
            return False
        if any(kw in haystack for kw in _ROLE_KEYWORDS):
            return True
        # Fall back to skill signal: a posting with real embedded/software
        # skills in its body is relevant even with an unusual title.
        return len(self.required_skills) >= 3

    def to_corpus_dict(self) -> dict:
        """Map to the recommendation engine's corpus schema."""
        return {
            "id": f"{self.source_portal}:{self.external_id}",
            "title": self.title,
            "company": self.company,
            "company_tier": self.company_tier,
            "location": self.location,
            "source_portal": self.source_portal,
            "source_url": self.source_url,
            "apply_url": self.apply_url,
            "description": self.description,
            "required_skills": ",".join(self.required_skills),
            "experience_min": self.experience_min,
            "experience_max": self.experience_max,
            "salary_min_lpa": self.salary_min_lpa,
            "salary_max_lpa": self.salary_max_lpa,
        }
