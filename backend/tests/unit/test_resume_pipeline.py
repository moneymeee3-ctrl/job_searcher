"""Unit tests — Resume parsing pipeline"""
import pytest
from app.resume.parser import parse_resume, detect_file_type, FileType
from app.resume.extractor import extract_skills, extract_experience
from app.resume.normalizer import build_profile

SAMPLE = """
Ram Sri Hari S
ram.srihari@test.com
+91 9876543210

Technical Skills: C, C++, Python, FreeRTOS, AUTOSAR, CAN, LIN, SPI, I2C, ARM Cortex-M, ISO 26262, ASIL-B, JTAG, GDB

Work Experience
Bosch Global Software Technologies
Embedded ASW Developer
July 2023 - Present

Education
Government College of Technology, Coimbatore
B.E. Electronics and Communication Engineering
2019 - 2023
"""

class TestParser:
    def test_txt_parse(self):
        doc = parse_resume("resume.txt", SAMPLE.encode())
        assert doc.raw_text.strip() != "" and not doc.is_scanned

    def test_pdf_magic_bytes(self):
        assert detect_file_type("r.pdf", b"%PDF-1.4 content") == FileType.PDF

    def test_txt_extension(self):
        assert detect_file_type("r.txt", b"content") == FileType.TXT

    def test_unsupported(self):
        assert detect_file_type("r.xyz", b"content") == FileType.UNSUPPORTED

    def test_empty_file(self):
        doc = parse_resume("r.txt", b"")
        assert doc.char_count == 0

class TestSkillExtractor:
    def test_extracts_c(self):
        skills = extract_skills(SAMPLE)
        assert "c" in skills.programming

    def test_extracts_cpp(self):
        skills = extract_skills(SAMPLE)
        assert "c++" in skills.programming

    def test_extracts_freertos(self):
        skills = extract_skills(SAMPLE)
        assert "freertos" in skills.rtos_os

    def test_extracts_can(self):
        skills = extract_skills(SAMPLE)
        assert "can" in skills.protocols

    def test_extracts_iso26262(self):
        skills = extract_skills(SAMPLE)
        assert "iso 26262" in skills.automotive

    def test_all_skills_is_union(self):
        skills = extract_skills(SAMPLE)
        for s in skills.programming: assert s in skills.all_skills
        for s in skills.protocols: assert s in skills.all_skills

    def test_no_false_positives_for_non_embedded(self):
        skills = extract_skills("React TypeScript Node.js CSS JavaScript REST API")
        assert "can" not in skills.protocols
        assert "freertos" not in skills.rtos_os

    def test_empty_returns_empty(self):
        skills = extract_skills("")
        assert skills.count() == 0

class TestExperienceExtractor:
    def test_finds_date_range(self):
        exp = extract_experience(SAMPLE)
        assert len(exp.work_entries) >= 1

    def test_total_years_positive(self):
        exp = extract_experience(SAMPLE)
        assert exp.total_years >= 0

    def test_education_extracted(self):
        exp = extract_experience(SAMPLE)
        assert len(exp.education) >= 1

    def test_empty_returns_zero(self):
        exp = extract_experience("")
        assert exp.total_years == 0.0

class TestProfileBuilder:
    def _build(self, text=SAMPLE):
        skills = extract_skills(text)
        exp = extract_experience(text)
        return build_profile(text, skills, exp)

    def test_embedded_engineer_detected(self):
        p = self._build()
        assert p.is_embedded_engineer is True

    def test_non_embedded_not_detected(self):
        p = self._build("React TypeScript Node.js CSS REST APIs developer frontend")
        assert p.is_embedded_engineer is False

    def test_email_extracted(self):
        p = self._build()
        assert "@" in p.email_hint

    def test_json_roundtrip(self):
        from app.resume.normalizer import CandidateProfile
        p = self._build()
        restored = CandidateProfile.from_json(p.to_json())
        assert restored.all_skills == p.all_skills and restored.embedded_domain_score == p.embedded_domain_score

    def test_embedded_score_high(self):
        p = self._build()
        assert p.embedded_domain_score >= 30
