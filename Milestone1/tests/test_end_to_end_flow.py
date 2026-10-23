"""
End-to-end flow tests verifying all authentication, password reset, and admin flows.
"""

import os
import tempfile
import pytest

from Milestone1.auth import (
    create_session_jwt,
    hash_password,
    hash_security_answer,
    validate_email,
    validate_mandatory_fields,
    validate_password,
    validate_password_confirmation,
    verify_password,
    verify_security_answer,
    verify_session_jwt,
)
from Milestone1.config import get_admin_credentials
from Milestone1.database import (
    SECURITY_QUESTIONS,
    create_user,
    get_all_registered_users,
    get_user_by_email,
    get_user_by_identifier,
    get_user_by_username,
    init_db,
    update_password,
)
from Milestone1.otp_service import create_otp_session, generate_otp, verify_otp_session


@pytest.fixture
def clean_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(db_path=path)
    yield path
    try:
        os.remove(path)
    except OSError:
        pass


class TestEndToEndMilestoneFlows:
    def test_signup_and_dual_login_flow(self, clean_db):
        """Test signup, duplicate rejection, and login via username OR email."""
        # Step 1: Validate inputs
        username = "alex_kumar"
        email = "alex@infosys.com"
        pwd = "ComplexPass@2026"
        confirm_pwd = "ComplexPass@2026"
        sq = SECURITY_QUESTIONS[0]
        sa = "Sunnyvale Elementary"

        assert validate_mandatory_fields(username=username, email=email, password=pwd, confirm_password=confirm_pwd, security_answer=sa)[0] is True
        assert validate_email(email)[0] is True
        assert validate_password(pwd)[0] is True
        assert validate_password_confirmation(pwd, confirm_pwd)[0] is True

        # Step 2: Register user
        pwd_hash = hash_password(pwd)
        sa_hash = hash_security_answer(sa)
        ok, msg = create_user(username, email, pwd_hash, sq, sa_hash, db_path=clean_db)
        assert ok is True

        # Duplicate username rejection
        ok_dup_u, msg_dup_u = create_user(username, "other@infosys.com", pwd_hash, sq, sa_hash, db_path=clean_db)
        assert ok_dup_u is False
        assert "Username 'alex_kumar' is already taken" in msg_dup_u

        # Duplicate email rejection
        ok_dup_e, msg_dup_e = create_user("alex2", email, pwd_hash, sq, sa_hash, db_path=clean_db)
        assert ok_dup_e is False
        assert "Email 'alex@infosys.com' is already registered" in msg_dup_e

        # Step 3: Login via Username
        user_by_u = get_user_by_identifier("alex_kumar", db_path=clean_db)
        assert user_by_u is not None
        assert verify_password(pwd, user_by_u["password_hash"]) is True
        token_u = create_session_jwt(user_by_u["username"], user_by_u["email"])
        valid_u, payload_u, _ = verify_session_jwt(token_u)
        assert valid_u is True
        assert payload_u["username"] == "alex_kumar"

        # Step 4: Login via Email
        user_by_e = get_user_by_identifier("alex@infosys.com", db_path=clean_db)
        assert user_by_e is not None
        assert verify_password(pwd, user_by_e["password_hash"]) is True
        token_e = create_session_jwt(user_by_e["username"], user_by_e["email"])
        valid_e, payload_e, _ = verify_session_jwt(token_e)
        assert valid_e is True
        assert payload_e["email"] == "alex@infosys.com"

        # Step 5: Failed login with wrong password
        assert verify_password("WrongPassword@999", user_by_u["password_hash"]) is False

        # Step 6: Failed login with non-existent user
        assert get_user_by_identifier("unknown_user", db_path=clean_db) is None

    def test_forgot_password_via_security_question_flow(self, clean_db):
        """Test password reset via Security Question route."""
        username = "priya_sharma"
        email = "priya@infosys.com"
        initial_pwd = "InitialPass@2026"
        sq = "What is your mother's maiden name?"
        sa = "Mukherjee"

        create_user(username, email, hash_password(initial_pwd), sq, hash_security_answer(sa), db_path=clean_db)

        # 1. Lookup question by username
        user = get_user_by_username("priya_sharma", db_path=clean_db)
        assert user is not None
        assert user["security_question"] == sq

        # 2. Check answer verification
        assert verify_security_answer("mukherjee", user["security_answer_hash"]) is True
        assert verify_security_answer(" MUKHERJEE ", user["security_answer_hash"]) is True
        assert verify_security_answer("WrongAnswer", user["security_answer_hash"]) is False

        # 3. Reset password
        new_pwd = "NewResetPass#2026"
        assert validate_password(new_pwd)[0] is True
        assert update_password(username, hash_password(new_pwd), db_path=clean_db) is True

        # 4. Verify login with new password succeeds and old password fails
        updated_user = get_user_by_username(username, db_path=clean_db)
        assert verify_password(new_pwd, updated_user["password_hash"]) is True
        assert verify_password(initial_pwd, updated_user["password_hash"]) is False

    def test_forgot_password_via_otp_flow(self, clean_db):
        """Test password reset via Email OTP route."""
        username = "rohit_verma"
        email = "rohit@infosys.com"
        old_pwd = "OldPassword@123"

        create_user(username, email, hash_password(old_pwd), SECURITY_QUESTIONS[1], hash_security_answer("Answer"), db_path=clean_db)

        # 1. Generate OTP and session
        otp = generate_otp()
        jwt_token, _ = create_otp_session(email, otp, db_path=clean_db)

        # 2. Verify OTP
        ok_v, msg_v = verify_otp_session(jwt_token, otp, email, db_path=clean_db)
        assert ok_v is True

        # 3. Update password
        new_pwd = "NewRohitPass@2026"
        assert validate_password(new_pwd)[0] is True
        assert update_password(email, hash_password(new_pwd), db_path=clean_db) is True

        # 4. Verify new password
        user = get_user_by_email(email, db_path=clean_db)
        assert verify_password(new_pwd, user["password_hash"]) is True
        assert verify_password(old_pwd, user["password_hash"]) is False

    def test_admin_portal_flow(self, clean_db):
        """Test dedicated admin credentials and registered user listing."""
        admin_u, admin_p = get_admin_credentials()
        assert admin_u != ""
        assert admin_p != ""

        # Create 2 regular users
        create_user("user_a", "usera@infosys.com", hash_password("PassA@1234"), SECURITY_QUESTIONS[0], hash_security_answer("A"), db_path=clean_db)
        create_user("user_b", "userb@infosys.com", hash_password("PassB@1234"), SECURITY_QUESTIONS[1], hash_security_answer("B"), db_path=clean_db)

        # Admin user listing
        user_list = get_all_registered_users(db_path=clean_db)
        assert len(user_list) == 2

        usernames = [u["username"] for u in user_list]
        emails = [u["email"] for u in user_list]
        assert "user_a" in usernames
        assert "user_b" in usernames
        assert "usera@infosys.com" in emails
        assert "userb@infosys.com" in emails

        # Strictly check no sensitive data is leaked
        for u in user_list:
            assert "password_hash" not in u
            assert "security_answer_hash" not in u
