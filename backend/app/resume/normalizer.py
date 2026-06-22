"""EMBEDHUNT AI — Profile Normalizer (assembles CandidateProfile from extracted components)"""
import json, re
from dataclasses import dataclass, field, asdict
from app.resume.extractor import ExtractedSkills, ExtractedExperience

_EMBEDDED_CORE = {"c","c++","rtos","freertos","embedded","firmware","arm","cortex-m","autosar","can","lin","spi","i2c","device driver","bare metal","iso 26262","linux kernel","bsp"}
_EMAIL = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
_PHONE = re.compile(r"(\+?\d[\d\s\-().]{7,}\d)")

@dataclass
class CandidateProfile:
    name_hint: str = ""; email_hint: str = ""; phone_hint: str = ""
    total_years_experience: float = 0.0
    current_role: str|None = None; current_company: str|None = None
    is_embedded_engineer: bool = False
    programming_languages: list[str] = field(default_factory=list)
    rtos_and_os: list[str] = field(default_factory=list)
    protocols: list[str] = field(default_factory=list)
    hardware_platforms: list[str] = field(default_factory=list)
    automotive_safety: list[str] = field(default_factory=list)
    tools_and_debug: list[str] = field(default_factory=list)
    software_concepts: list[str] = field(default_factory=list)
    all_skills: list[str] = field(default_factory=list)
    skill_count: int = 0; embedded_domain_score: int = 0
    highest_degree: str = ""; field_of_study: str = ""; graduation_year: int|None = None

    def to_json(self) -> str: return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, s: str) -> "CandidateProfile": return cls(**json.loads(s))

def build_profile(raw_text: str, skills: ExtractedSkills, exp: ExtractedExperience) -> CandidateProfile:
    em = _EMAIL.search(raw_text); ph = _PHONE.search(raw_text)
    name = _guess_name(raw_text)
    edu = exp.education[0] if exp.education else None
    matched_core = set(skills.all_skills) & _EMBEDDED_CORE
    score = min(100, int(len(matched_core) / len(_EMBEDDED_CORE) * 100))
    if skills.automotive: score = min(100, score + 10)
    if exp.total_years > 2: score = min(100, score + 5)
    return CandidateProfile(
        name_hint=name, email_hint=em.group(0) if em else "", phone_hint=ph.group(0).strip() if ph else "",
        total_years_experience=exp.total_years, current_role=exp.current_role, current_company=exp.current_company,
        is_embedded_engineer=score >= 40 or len(matched_core) >= 4,
        programming_languages=skills.programming, rtos_and_os=skills.rtos_os,
        protocols=skills.protocols, hardware_platforms=skills.hardware,
        automotive_safety=skills.automotive, tools_and_debug=skills.tools,
        software_concepts=skills.concepts, all_skills=skills.all_skills,
        skill_count=skills.count(), embedded_domain_score=score,
        highest_degree=edu.degree if edu else "", field_of_study=edu.field_of_study if edu else "",
        graduation_year=edu.year if edu else None,
    )

def _guess_name(text: str) -> str:
    for line in [l.strip() for l in text.split("\n") if l.strip()][:5]:
        words = line.split()
        if 2 <= len(words) <= 4 and not any(c.isdigit() for c in line):
            if not re.search(r"[@|/\\(]|resume|curriculum|cv\b", line, re.I): return line
    return ""
