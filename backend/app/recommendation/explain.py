"""EMBEDHUNT AI — Gap Explainer with learning resources"""
from dataclasses import dataclass, field
from enum import Enum
from app.recommendation.matcher import WEIGHTS, MatchScore

class GapPriority(str, Enum): HIGH="HIGH"; MEDIUM="MEDIUM"; LOW="LOW"

def _priority(cat: str) -> GapPriority:
    w = WEIGHTS.get(cat, 0)
    return GapPriority.HIGH if w>=20 else GapPriority.MEDIUM if w>=15 else GapPriority.LOW

RESOURCES = {
    "c":["K&R C Programming Language","Embedded C in Practice"],"c++":["Effective C++","C++ Core Guidelines"],
    "python":["Python for Engineers (Real Python)"],"freertos":["FreeRTOS.org docs","Mastering FreeRTOS Kernel (free PDF)"],
    "rtos":["Barr Group RTOS Concepts"],"autosar":["Vector AUTOSAR tutorial","AUTOSAR.org standards"],
    "linux kernel":["Linux Device Drivers 3rd Ed (free)","Bootlin kernel training"],
    "can":["CiA CAN protocol guide"],"lin":["LIN Consortium spec"],"spi":["Analog Devices SPI guide"],
    "i2c":["NXP I2C spec (free)"],"uart":["Circuit Digest UART tutorial"],
    "arm":["ARM Cortex-M Programming Guide"],"cortex-m":["Definitive Guide to ARM Cortex-M"],
    "iso 26262":["Vector ISO 26262 overview"],"asil":["TÜV ASIL decomposition guide"],
    "jtag":["Lauterbach JTAG guide"],"gdb":["Embedded GDB tutorial"],
    "device driver":["Linux Device Drivers 3rd Ed"],"bsp":["Yocto BSP tutorial"],
    "misra c":["MISRA C 2012 Guidelines"],
}
DEFAULT_RES = ["Search Udemy, YouTube, or vendor documentation"]

@dataclass
class SkillGap:
    skill: str; category: str; priority: GapPriority
    learning_resources: list[str]; in_required: bool

@dataclass
class GapAnalysis:
    job_title: str; total_score: int; recommendation: str
    high: list[SkillGap] = field(default_factory=list)
    medium: list[SkillGap] = field(default_factory=list)
    low: list[SkillGap] = field(default_factory=list)
    matched_skills: list[str] = field(default_factory=list)
    immediate_focus: list[str] = field(default_factory=list)
    upskill_weeks: int = 0; summary: str = ""
    @property
    def all_gaps(self): return self.high + self.medium + self.low

def analyze_gaps(match: MatchScore, job_title: str) -> GapAnalysis:
    skill_to_cat = {s:cs.category for cs in match.category_scores for s in cs.job_skills}
    explicit = set(match.job_required_skills)
    high, medium, low = [], [], []
    for skill in match.missing_skills:
        cat = skill_to_cat.get(skill, "concepts")
        pri = _priority(cat)
        gap = SkillGap(skill, cat, pri, RESOURCES.get(skill, DEFAULT_RES), skill in explicit)
        (high if pri==GapPriority.HIGH else medium if pri==GapPriority.MEDIUM else low).append(gap)
    for tier in [high, medium, low]: tier.sort(key=lambda g: (not g.in_required, g.skill))
    weeks = min(52, len(high)*3 + len(medium)*1)
    summary = _summarize(match.total_score, high, medium, low, job_title)
    return GapAnalysis(job_title, match.total_score, match.recommendation, high, medium, low, match.matched_skills, [g.skill for g in high[:3]], weeks, summary)

def _summarize(score, high, medium, low, title):
    if not high and not medium: return f"Well-qualified for {title}. No critical gaps."
    parts = [f"Score: {score}/99 for {title}."]
    if high: parts.append(f"{len(high)} high-priority gap(s): {', '.join(g.skill for g in high[:4])}.")
    if medium: parts.append(f"{len(medium)} medium gap(s): {', '.join(g.skill for g in medium[:3])}.")
    parts.append(f"Estimated upskill: ~{len(high)*3+len(medium)} weeks.")
    return " ".join(parts)
