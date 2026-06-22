"""EMBEDHUNT AI — Roadmap Planner"""
from dataclasses import dataclass, field
from enum import Enum

class SkillLevel(str, Enum): BEGINNER="beginner"; INTERMEDIATE="intermediate"; ADVANCED="advanced"
class TaskStatus(str, Enum): PENDING="pending"; IN_PROGRESS="in_progress"; COMPLETED="completed"

SKILL_HOURS = {
    "c": 40, "c++": 60, "python": 30, "freertos": 35, "rtos": 35, "autosar": 80,
    "linux kernel": 100, "linux": 60, "yocto": 50, "bsp": 45, "device driver": 60,
    "can": 20, "lin": 15, "spi": 10, "i2c": 10, "uart": 8, "ethernet": 25,
    "arm": 30, "cortex-m": 35, "iso 26262": 40, "asil": 20, "misra c": 20,
    "jtag": 15, "gdb": 20, "cmake": 15, "git": 10, "docker": 20,
    "bootloader": 40, "bare metal": 30, "modbus": 15, "mqtt": 15,
}
DEFAULT_HOURS = 25

SKILL_RESOURCES = {
    "c": [{"title":"K&R C Programming Language","type":"book","url":"https://www.amazon.com/Programming-Language-2nd-Brian-Kernighan/dp/0131103628"},{"title":"Embedded C Programming","type":"video","url":"https://www.youtube.com/results?search_query=embedded+c+programming"}],
    "c++": [{"title":"Effective C++ (Scott Meyers)","type":"book","url":"https://www.amazon.com/Effective-Specific-Improve-Programs-Designs/dp/0321334876"}],
    "freertos": [{"title":"Mastering the FreeRTOS Kernel","type":"book","url":"https://www.freertos.org/Documentation/RTOS_book.html"},{"title":"FreeRTOS Official Docs","type":"docs","url":"https://freertos.org"}],
    "autosar": [{"title":"AUTOSAR Classic Tutorial (Vector)","type":"course","url":"https://www.vector.com/int/en/know-how/training/"},{"title":"AUTOSAR.org Standards","type":"docs","url":"https://www.autosar.org"}],
    "linux kernel": [{"title":"Linux Device Drivers 3rd Ed (free)","type":"book","url":"https://lwn.net/Kernel/LDD3/"},{"title":"Bootlin Kernel Training","type":"course","url":"https://bootlin.com/training/kernel"}],
    "iso 26262": [{"title":"ISO 26262 Overview (Vector)","type":"course","url":"https://www.vector.com"},{"title":"Functional Safety in Automotive","type":"course","url":"https://www.udemy.com"}],
    "can": [{"title":"CAN in Automation (CiA)","type":"docs","url":"https://www.can-cia.org"},{"title":"Vector CAN Protocol Basics","type":"video","url":"https://www.vector.com"}],
    "arm": [{"title":"Definitive Guide to Cortex-M (Yiu)","type":"book","url":"https://www.amazon.com"},{"title":"ARM Architecture Reference Manual","type":"docs","url":"https://developer.arm.com"}],
    "yocto": [{"title":"Yocto Project Documentation","type":"docs","url":"https://docs.yoctoproject.org"},{"title":"Bootlin Yocto Training","type":"course","url":"https://bootlin.com/training/yocto"}],
    "device driver": [{"title":"Linux Device Drivers 3rd Ed","type":"book","url":"https://lwn.net/Kernel/LDD3/"}],
    "gdb": [{"title":"GDB Embedded Tutorial","type":"video","url":"https://www.youtube.com/results?search_query=gdb+embedded+debugging"}],
    "misra c": [{"title":"MISRA C:2012 Guidelines","type":"book","url":"https://www.misra.org.uk"}],
}
DEFAULT_RESOURCES = [{"title":"Search Udemy, YouTube or vendor documentation","type":"general","url":"https://www.udemy.com"}]

@dataclass
class LearningTask:
    skill: str; priority: int; estimated_hours: int; level: SkillLevel
    resources: list[dict]; status: TaskStatus = TaskStatus.PENDING
    weeks_estimate: int = 0

@dataclass
class LearningRoadmap:
    user_id: str; job_title: str; current_score: int; projected_score: int
    total_hours: int; total_weeks: int
    tasks: list[LearningTask] = field(default_factory=list)
    immediate_actions: list[str] = field(default_factory=list)
    summary: str = ""

def generate_roadmap(user_id: str, missing_skills: list[str], current_score: int, job_title: str) -> LearningRoadmap:
    tasks = []
    for i, skill in enumerate(missing_skills):
        hours = SKILL_HOURS.get(skill, DEFAULT_HOURS)
        level = SkillLevel.BEGINNER if hours <= 20 else SkillLevel.INTERMEDIATE if hours <= 50 else SkillLevel.ADVANCED
        tasks.append(LearningTask(
            skill=skill, priority=i+1, estimated_hours=hours, level=level,
            resources=SKILL_RESOURCES.get(skill, DEFAULT_RESOURCES),
            weeks_estimate=max(1, hours // 10)
        ))
    tasks.sort(key=lambda t: t.priority)
    total_hours = sum(t.estimated_hours for t in tasks)
    total_weeks = min(52, total_hours // 10)
    projected = min(99, current_score + len(missing_skills) * 5)
    immediate = [t.skill for t in tasks[:3]]
    summary = f"Learn {len(tasks)} skills in ~{total_weeks} weeks to go from {current_score} → {projected} match score for {job_title}."
    return LearningRoadmap(user_id, job_title, current_score, projected, total_hours, total_weeks, tasks, immediate, summary)
