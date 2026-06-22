"""EMBEDHUNT AI — Skill & Experience Extractor"""
import json, re
from dataclasses import dataclass, field, asdict
from datetime import datetime

# ── Skill Taxonomy (120+ embedded skills) ─────────────────────────────────────
PROGRAMMING = {"c","c++","python","rust","assembly","ada","matlab","simulink","java","kotlin"}
RTOS_OS = {"freertos","rtos","threadx","vxworks","zephyr","qnx","autosar","misra c","linux","linux kernel","embedded linux","yocto","buildroot","bare metal"}
PROTOCOLS = {"can","can-fd","lin","flexray","spi","i2c","i2s","uart","usart","usb","ethernet","tcp/ip","mqtt","someip","some/ip","doip","uds","modbus","ble","bluetooth","wi-fi","zigbee"}
HARDWARE = {"arm","arm cortex","cortex-m","cortex-m4","cortex-m7","cortex-a","cortex-r","risc-v","stm32","nxp","s32k","renesas","rh850","snapdragon","qualcomm","pic","avr","esp32","nordic","ti","fpga","vhdl","verilog"}
AUTOMOTIVE = {"iso 26262","asil","asil-b","asil-d","sotif","autosar","bsw","swc","rte","uds","adas","esc","abs","functional safety"}
TOOLS = {"jtag","swd","lauterbach","trace32","gdb","oscilloscope","cmake","make","jenkins","ci/cd","docker","git","svn","jira","googletest","gtest","pc-lint","polyspace","coverity"}
CONCEPTS = {"device driver","bsp","board support package","bootloader","dma","interrupt","memory management","mmu","power management","ota","cryptography","secure boot","state machine","pid controller"}
ALL_SKILLS = PROGRAMMING|RTOS_OS|PROTOCOLS|HARDWARE|AUTOMOTIVE|TOOLS|CONCEPTS

ALIASES = {"c language":"c","embedded c":"c","c programming":"c","canfd":"can-fd","iso26262":"iso 26262","iso-26262":"iso 26262","free rtos":"freertos","risc v":"risc-v","cortex m":"cortex-m","ci cd":"ci/cd"}

@dataclass
class ExtractedSkills:
    programming: list[str] = field(default_factory=list)
    rtos_os: list[str] = field(default_factory=list)
    protocols: list[str] = field(default_factory=list)
    hardware: list[str] = field(default_factory=list)
    automotive: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    concepts: list[str] = field(default_factory=list)
    all_skills: list[str] = field(default_factory=list)
    def to_csv(self) -> str: return ", ".join(self.all_skills)
    def count(self) -> int: return len(self.all_skills)

@dataclass
class WorkEntry:
    company: str; role: str; start_year: int|None; end_year: int|None; duration_months: int|None

@dataclass
class EducationEntry:
    institution: str; degree: str; field_of_study: str; year: int|None

@dataclass
class ExtractedExperience:
    work_entries: list[WorkEntry] = field(default_factory=list)
    education: list[EducationEntry] = field(default_factory=list)
    total_years: float = 0.0
    current_role: str|None = None
    current_company: str|None = None
    def to_json(self) -> str: return json.dumps(asdict(self))

def _normalize(text: str) -> str:
    t = re.sub(r"\s+", " ", text.lower().strip())
    for alias, canon in ALIASES.items(): t = t.replace(alias, canon)
    return t

def extract_skills(raw_text: str) -> ExtractedSkills:
    if not raw_text: return ExtractedSkills()
    text = _normalize(raw_text)

    def _find(skill_set):
        found = set()
        for skill in skill_set:
            esc = re.escape(skill)
            starts_w = skill[0].isalnum(); ends_w = skill[-1].isalnum()
            if len(skill) <= 2 and skill.isalpha(): pat = rf"\b{esc}\b"
            elif starts_w and ends_w: pat = rf"\b{esc}\b"
            else: pat = rf"(?<![a-zA-Z0-9]){esc}(?![a-zA-Z0-9])"
            if re.search(pat, text): found.add(skill)
        return sorted(found)

    prog=_find(PROGRAMMING); rtos=_find(RTOS_OS); proto=_find(PROTOCOLS)
    hw=_find(HARDWARE); auto=_find(AUTOMOTIVE); tools=_find(TOOLS); conc=_find(CONCEPTS)
    all_d = {s:None for lst in [prog,rtos,proto,hw,auto,tools,conc] for s in lst}
    return ExtractedSkills(prog,rtos,proto,hw,auto,tools,conc,list(all_d.keys()))

_DATE = re.compile(r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)?[\w\s]*?(\d{4})\s*[-–—to]+\s*(?:present|current|now|till\s*date|(\d{4}))", re.I)
_DEGREE = re.compile(r"\b(b\.?e\.?|b\.?tech\.?|m\.?e\.?|m\.?tech\.?|b\.?sc\.?|m\.?sc\.?|bachelor|master|phd|mba|diploma)\b", re.I)
_KNOWN = {"bosch","qualcomm","nvidia","nxp","ti","texas instruments","continental","infineon","stmicroelectronics","renesas","harman","kpit","tata elxsi","bgsw"}
_ROLE_KW = re.compile(r"\b(engineer|developer|architect|analyst|manager|lead|senior|intern|specialist)\b", re.I)

def extract_experience(raw_text: str) -> ExtractedExperience:
    if not raw_text: return ExtractedExperience()
    lines = raw_text.split("\n"); entries = []; curr_year = datetime.now().year
    for i, line in enumerate(lines):
        m = _DATE.search(line)
        if not m: continue
        sy = int(m.group(1))
        ey = int(m.group(2)) if m.group(2) else None
        dur = max(0, ((ey or curr_year) - sy) * 12)
        ctx = lines[max(0,i-3):i+4]
        co = next((l.strip() for l in ctx if any(k in l.lower() for k in _KNOWN)), "")
        ro = next((l.strip() for l in ctx if _ROLE_KW.search(l)), "")
        entries.append(WorkEntry(co[:100] or "Unknown", ro[:150] or "Unknown", sy, ey, dur))
    edu = []
    for i, line in enumerate(lines):
        if not _DEGREE.search(line): continue
        ctx = " ".join(lines[max(0,i-1):i+3])
        yr = int(m2.group(0)) if (m2:=re.search(r"\b(19|20)\d{2}\b", ctx)) else None
        field = m3.group(0).title() if (m3:=re.search(r"\b(electronics?|computer science|electrical|mechanical|communication|embedded)\b", ctx, re.I)) else ""
        inst = next((l.strip() for l in lines[max(0,i-2):i+2] if any(k in l.lower() for k in ["college","university","institute"])), "")
        edu.append(EducationEntry(inst or "Unknown", _DEGREE.search(line).group(0).upper(), field, yr))
    total = min(sum(e.duration_months or 0 for e in entries) / 12, 40.0)
    curr = next((e for e in entries if e.end_year is None), None) or (entries[-1] if entries else None)
    return ExtractedExperience(entries, edu[:3], round(total,1), curr.role if curr else None, curr.company if curr else None)
