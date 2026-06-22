"""Unit tests — Auth module"""
import pytest
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token, create_refresh_token, decode_token, TokenType, create_email_verify_token
from app.auth.permissions import UserRole, ROLE_HIERARCHY

class TestPassword:
    def test_hash_differs_from_plain(self):
        h = hash_password("Secret1!")
        assert h != "Secret1!" and len(h) > 40

    def test_verify_correct(self):
        h = hash_password("Secret1!")
        assert verify_password("Secret1!", h)

    def test_reject_wrong(self):
        h = hash_password("Secret1!")
        assert not verify_password("Wrong1!", h)

    def test_unique_hashes(self):
        h1, h2 = hash_password("Same1!"), hash_password("Same1!")
        assert h1 != h2  # bcrypt salt

class TestJWT:
    def test_access_token_roundtrip(self):
        token = create_access_token("uid-1", "candidate")
        payload = decode_token(token, TokenType.ACCESS)
        assert payload["sub"] == "uid-1" and payload["role"] == "candidate"

    def test_refresh_token_roundtrip(self):
        token = create_refresh_token("uid-2")
        payload = decode_token(token, TokenType.REFRESH)
        assert payload["sub"] == "uid-2"

    def test_type_mismatch_raises(self):
        from fastapi import HTTPException
        token = create_access_token("uid-3", "candidate")
        with pytest.raises(HTTPException) as exc: decode_token(token, TokenType.REFRESH)
        assert exc.value.status_code == 401

    def test_tampered_token_raises(self):
        from fastapi import HTTPException
        token = create_access_token("uid-4", "candidate") + "tampered"
        with pytest.raises(HTTPException): decode_token(token, TokenType.ACCESS)

    def test_email_verify_token(self):
        token = create_email_verify_token("test@example.com")
        payload = decode_token(token, TokenType.EMAIL_VERIFY)
        assert payload["sub"] == "test@example.com"

class TestRBAC:
    def test_hierarchy_order(self):
        assert ROLE_HIERARCHY[UserRole.PLATFORM_ADMIN] > ROLE_HIERARCHY[UserRole.COMPANY_ADMIN]
        assert ROLE_HIERARCHY[UserRole.COMPANY_ADMIN] > ROLE_HIERARCHY[UserRole.RECRUITER]
        assert ROLE_HIERARCHY[UserRole.RECRUITER] > ROLE_HIERARCHY[UserRole.CANDIDATE]

class TestAuthSchemas:
    def test_valid_register(self):
        from app.schemas.auth import RegisterRequest
        r = RegisterRequest(email="ram@embedhunt.ai", username="ram_sri", password="Bosch2024!", first_name="Ram", last_name="Sri")
        assert r.username == "ram_sri" and r.email == "ram@embedhunt.ai"

    def test_weak_password_rejected(self):
        from app.schemas.auth import RegisterRequest
        from pydantic import ValidationError
        with pytest.raises(ValidationError): RegisterRequest(email="x@x.com", username="ram", password="weak", first_name="A", last_name="B")

    def test_short_username_rejected(self):
        from app.schemas.auth import RegisterRequest
        from pydantic import ValidationError
        with pytest.raises(ValidationError): RegisterRequest(email="x@x.com", username="ab", password="Secure1!", first_name="A", last_name="B")
