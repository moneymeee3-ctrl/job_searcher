"""Unit tests for Module 3 — skill extractor with confidence scoring."""
from app.ai.skill_extractor import (
    ALL_SKILLS,
    ExtractedSkill,
    SkillExtractor,
    get_skill_extractor,
)

RESUME = """
Ram Kumar — Embedded Software Engineer

Summary
Embedded engineer with 6 years of experience in automotive firmware.

Technical Skills:
C, C++, Python, FreeRTOS, CAN, CAN-FD, SPI, I2C, ARM Cortex-M4, STM32,
AUTOSAR, ISO 26262, JTAG, GDB, Git, Device Driver, Bootloader

Experience
Bosch — Senior Firmware Engineer (2019 - Present)
Developed FreeRTOS-based firmware on ARM Cortex-M4. Implemented CAN and SPI
drivers. 6 years of C and C++ development.

Education
B.E. Electronics, 2018
"""


def test_taxonomy_has_300_plus_skills():
    assert len(ALL_SKILLS) >= 300


def test_extract_returns_extracted_skill_objects():
    skills = SkillExtractor().extract(RESUME)
    assert skills
    assert all(isinstance(s, ExtractedSkill) for s in skills)
    names = {s.name for s in skills}
    assert {"c", "c++", "freertos", "can", "spi", "arm cortex", "autosar"} & names


def test_confidence_within_bounds():
    for s in SkillExtractor().extract(RESUME):
        assert 0.0 <= s.confidence <= 1.0


def test_skills_section_boosts_confidence():
    ex = SkillExtractor()
    in_section = "Technical Skills: FreeRTOS, CAN, SPI"
    body_only = "We used freertos somewhere in the project narrative text."
    c_section = next(s for s in ex.extract(in_section) if s.name == "freertos")
    c_body = next(s for s in ex.extract(body_only) if s.name == "freertos")
    assert c_section.confidence > c_body.confidence
    assert c_section.in_skills_section


def test_repeated_mentions_increase_confidence():
    ex = SkillExtractor()
    once = next(s for s in ex.extract("Worked with can bus once.") if s.name == "can")
    many = next(s for s in ex.extract("can can can can bus everywhere") if s.name == "can")
    assert many.mentions > once.mentions
    assert many.confidence >= once.confidence


def test_near_experience_flag():
    skills = SkillExtractor().extract(RESUME)
    c = next(s for s in skills if s.name == "c")
    assert c.near_experience


def test_extract_grouped_buckets_by_category():
    grouped = SkillExtractor().extract_grouped(RESUME)
    assert set(grouped.keys()) >= {"programming", "protocols", "automotive"}
    prog_names = {s.name for s in grouped["programming"]}
    assert "c" in prog_names


def test_empty_text_returns_empty():
    assert SkillExtractor().extract("") == []


def test_no_false_positive_substring():
    # "scan" must not match "can"; "arma" must not match "arm"
    skills = {s.name for s in SkillExtractor().extract("We ran a scan of the armature.")}
    assert "can" not in skills
    assert "arm" not in skills


def test_singleton_accessor():
    assert get_skill_extractor() is get_skill_extractor()
