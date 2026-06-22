"""EMBEDHUNT AI — Interview Question Generator"""
from dataclasses import dataclass, field
from app.interview.question_bank import get_questions_for_skills, get_all_questions_flat

@dataclass
class InterviewKit:
    job_title: str; company: str; readiness_score: int
    questions_by_skill: dict[str, list[dict]]
    all_questions: list[dict]
    focus_skills: list[str]
    coding_topics: list[str]
    checklist: list[str]
    total_questions: int
    preparation_summary: str

CODING_TOPICS = {
    "c": ["Bit manipulation","Linked list","Ring buffer","State machine","Sorting algorithms"],
    "c++": ["Templates","STL containers","Smart pointers","Design patterns","Move semantics"],
    "python": ["File I/O","Regular expressions","Data structures","OOP","Testing with pytest"],
    "rtos": ["Task synchronization","Deadlock prevention","ISR-safe operations","Timer callbacks"],
    "linux kernel": ["Kernel module","Character driver","Proc filesystem","Sysfs attributes"],
    "arm": ["Startup code","Linker script","Assembly instructions","Cache management"],
}

INTERVIEW_CHECKLIST = [
    "Review all matched skills with depth",
    "Practice coding problems without IDE assistance",
    "Study company's product domain (automotive/semiconductor/IoT)",
    "Prepare 2-3 project examples demonstrating embedded experience",
    "Review system design for embedded systems",
    "Practice explaining trade-offs (latency vs throughput, power vs performance)",
    "Study recent papers/patents from target company",
    "Prepare questions for the interviewer about tech stack and team",
]

def generate_interview_kit(job_title: str, company: str, matched_skills: list[str], match_score: int) -> InterviewKit:
    questions_by_skill = get_questions_for_skills(matched_skills, max_per_skill=3)
    all_questions = get_all_questions_flat(matched_skills)
    coding_topics = []
    for skill in matched_skills:
        coding_topics.extend(CODING_TOPICS.get(skill, []))
    coding_topics = list(dict.fromkeys(coding_topics))[:10]
    readiness = min(99, match_score + (len(questions_by_skill) * 2))
    summary = (
        f"You matched {len(matched_skills)} required skills for {job_title} at {company}. "
        f"Estimated interview readiness: {readiness}/99. "
        f"Focus on: {', '.join(matched_skills[:4])}."
    )
    return InterviewKit(
        job_title=job_title, company=company, readiness_score=readiness,
        questions_by_skill=questions_by_skill, all_questions=all_questions,
        focus_skills=matched_skills[:5], coding_topics=coding_topics,
        checklist=INTERVIEW_CHECKLIST, total_questions=len(all_questions),
        preparation_summary=summary,
    )
