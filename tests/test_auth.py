"""
Unit tests for authentication, field validation, bcrypt hashing, and JWT tokens.
"""

import time
import pytest

from Milestone1.auth import (
    create_session_jwt,
    hash_password,
    hash_security_answer,
    normalize_security_answer,
    validate_email,
    validate_mandatory_fields,
    validate_password,
    validate_password_confirmation,
    verify_password,
    verify_security_answer,
    verify_session_jwt,
)


class TestFieldValidations:
    def test_mandatory_fields_success(self):
        ok, msg = validate_mandatory_fields(
            username="john_doe",
            email="john@infosys.com",
            password="Password@123"
        )
        assert ok is True
        assert msg == ""

    def test_mandatory_fields_empty_fails(self):
        ok, msg = validate_mandatory_fields(
            username="john_doe",
            email="   ",
            password="Password@123"
        )
        assert ok is False
        assert "Email" in msg

    def test_email_validation_milestone_rules(self):
        # Valid cases per Milestone Step 8 (at least 2 before @, 2 between @ and dot, 2 after dot)
        assert validate_email("ab@cd.ef")[0] is True
        assert validate_email("user@infosys.com")[0] is True
        assert validate_email("john.doe@sub.company.org")[0] is True

        # Invalid cases
        # Less than 2 before @
        ok, msg = validate_email("a@cd.ef")
        assert ok is False
        assert "at least 2 characters before" in msg

        # Less than 2 between @ and dot
        ok, msg = validate_email("ab@c.ef")
        assert ok is False
        assert "at least 2 characters between" in msg

        # Less than 2 after dot
        ok, msg = validate_email("ab@cd.e")
        assert ok is False
        assert "at least 2 characters after" in msg

        # Missing @
        assert validate_email("plainaddress.com")[0] is False

        # Missing dot
        assert validate_email("user@nodotcom")[0] is False

    def test_password_complexity_rules(self):
        # Valid password (>=8 chars, upper, lower, number, special symbol)
        assert validate_password("Pass@1234")[0] is True
        assert validate_password("Infosys#2026")[0] is True
        assert validate_password("Secure_Pass1")[0] is True

        # Too short (<8 chars)
        ok, msg = validate_password("Pass@1")
        assert ok is False
        assert "at least 8 characters" in msg

        # Missing uppercase
        ok, msg = validate_password("pass@1234")
        assert ok is False
        assert "uppercase" in msg

        # Missing lowercase
        ok, msg = validate_password("PASS@1234")
        assert ok is False
        assert "lowercase" in msg

        # Missing number
        ok, msg = validate_password("Password@xyz")
        assert ok is False
        assert "number" in msg

        # Missing special symbol
        ok, msg = validate_password("Password1234")
        assert ok is False
        assert "special symbol" in msg

    def test_password_confirmation(self):
        assert validate_password_confirmation("Pass@123", "Pass@123")[0] is True
        ok, msg = validate_password_confirmation("Pass@123", "Pass@999")
        assert ok is False
        assert "do not match" in msg


class TestBcryptHashing:
    def test_password_hashing_and_verification(self):
        pwd = "SecretPassword@2026"
        hashed = hash_password(pwd)

        assert hashed != pwd
        assert hashed.startswith("$2b$") or hashed.startswith("$2a$")

        # Correct password verifies
        assert verify_password(pwd, hashed) is True

        # Incorrect password fails
        assert verify_password("WrongPassword@2026", hashed) is False

        # Verify salts differ across runs
        hashed_2 = hash_password(pwd)
        assert hashed != hashed_2
        assert verify_password(pwd, hashed_2) is True

    def test_security_answer_normalization_and_verification(self):
        raw_answer = "  Fluffy The Cat  "
        normalized = normalize_security_answer(raw_answer)
        assert normalized == "fluffy the cat"

        hashed = hash_security_answer(raw_answer)

        # Answers in different casings and spaces should verify successfully
        assert verify_security_answer("fluffy the cat", hashed) is True
        assert verify_security_answer("FLUFFY THE CAT", hashed) is True
        assert verify_security_answer("   Fluffy   The   Cat   ", hashed) is True

        # Wrong answer fails
        assert verify_security_answer("dog", hashed) is False


class TestJWTSession:
    def test_jwt_session_lifecycle(self):
        token = create_session_jwt(username="jane_doe", email="jane@infosys.com", role="user", expires_in_hours=1)
        assert isinstance(token, str)

        # Successful verification
        is_valid, payload, msg = verify_session_jwt(token)
        assert is_valid is True
        assert payload is not None
        assert payload["username"] == "jane_doe"
        assert payload["email"] == "jane@infosys.com"
        assert payload["role"] == "user"

    def test_jwt_tampering_rejected(self):
        token = create_session_jwt(username="john_doe", email="john@infosys.com")
        tampered_token = token[:-5] + "xxxxx"

        is_valid, payload, msg = verify_session_jwt(tampered_token)
        assert is_valid is False
        assert payload is None
        assert "Invalid session token" in msg

    def test_jwt_expiration(self):
        # Create token that already expired (negative hours)
        token = create_session_jwt(username="expired_user", email="exp@test.com", expires_in_hours=-1)
        is_valid, payload, msg = verify_session_jwt(token)
        assert is_valid is False
        assert "expired" in msg.lower()
