"""
Integration tests for the unified SQLite database module.
"""

import os
import tempfile
import time
import pytest

from Milestone1.auth import hash_password, hash_security_answer, verify_password
from Milestone1.database import (
    SECURITY_QUESTIONS,
    check_email_exists,
    check_username_exists,
    create_user,
    get_all_registered_users,
    get_user_by_email,
    get_user_by_identifier,
    get_user_by_username,
    init_db,
    store_otp_record,
    update_password,
    verify_and_consume_otp_record,
)


@pytest.fixture
def temp_db():
    """Create an isolated temporary SQLite database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(db_path=path)
    yield path
    try:
        os.remove(path)
    except OSError:
        pass


class TestDatabaseOperations:
    def test_create_and_fetch_user(self, temp_db):
        pwd_hash = hash_password("Password@123")
        ans_hash = hash_security_answer("Fluffy")

        ok, msg = create_user(
            username="testuser",
            email="testuser@infosys.com",
            password_hash=pwd_hash,
            security_question=SECURITY_QUESTIONS[0],
            security_answer_hash=ans_hash,
            db_path=temp_db
        )
        assert ok is True
        assert "registered successfully" in msg

        # Fetch by username
        user_by_uname = get_user_by_username("testuser", db_path=temp_db)
        assert user_by_uname is not None
        assert user_by_uname["username"] == "testuser"
        assert user_by_uname["email"] == "testuser@infosys.com"

        # Fetch by email
        user_by_mail = get_user_by_email("testuser@infosys.com", db_path=temp_db)
        assert user_by_mail is not None
        assert user_by_mail["username"] == "testuser"

        # Unified identifier lookup (by username or email)
        assert get_user_by_identifier("testuser", db_path=temp_db) is not None
        assert get_user_by_identifier("TESTUSER@INFOSYS.COM", db_path=temp_db) is not None
        assert get_user_by_identifier("nonexistent", db_path=temp_db) is None

    def test_duplicate_username_rejection(self, temp_db):
        pwd_hash = hash_password("Password@123")
        ans_hash = hash_security_answer("Fluffy")

        # Create first user
        create_user("alice", "alice@infosys.com", pwd_hash, SECURITY_QUESTIONS[0], ans_hash, db_path=temp_db)

        # Attempt to create user with same username but different email
        ok, msg = create_user("alice", "alice2@infosys.com", pwd_hash, SECURITY_QUESTIONS[0], ans_hash, db_path=temp_db)
        assert ok is False
        assert "Username 'alice' is already taken" in msg

    def test_duplicate_email_rejection(self, temp_db):
        pwd_hash = hash_password("Password@123")
        ans_hash = hash_security_answer("Fluffy")

        # Create first user
        create_user("bob", "bob@infosys.com", pwd_hash, SECURITY_QUESTIONS[0], ans_hash, db_path=temp_db)

        # Attempt to create user with different username but same email
        ok, msg = create_user("bob_alt", "bob@infosys.com", pwd_hash, SECURITY_QUESTIONS[0], ans_hash, db_path=temp_db)
        assert ok is False
        assert "Email 'bob@infosys.com' is already registered" in msg

    def test_password_update(self, temp_db):
        old_pwd_hash = hash_password("OldPassword@123")
        new_pwd_hash = hash_password("NewPassword@2026")
        ans_hash = hash_security_answer("Fluffy")

        create_user("charlie", "charlie@infosys.com", old_pwd_hash, SECURITY_QUESTIONS[0], ans_hash, db_path=temp_db)

        # Update by username
        updated = update_password("charlie", new_pwd_hash, db_path=temp_db)
        assert updated is True

        user = get_user_by_username("charlie", db_path=temp_db)
        assert verify_password("NewPassword@2026", user["password_hash"]) is True
        assert verify_password("OldPassword@123", user["password_hash"]) is False

    def test_admin_get_all_users_never_exposes_passwords(self, temp_db):
        pwd_hash = hash_password("Secret@123")
        ans_hash = hash_security_answer("Answer")

        create_user("user1", "user1@infosys.com", pwd_hash, SECURITY_QUESTIONS[0], ans_hash, db_path=temp_db)
        create_user("user2", "user2@infosys.com", pwd_hash, SECURITY_QUESTIONS[1], ans_hash, db_path=temp_db)

        users = get_all_registered_users(db_path=temp_db)
        assert len(users) == 2

        for u in users:
            assert "username" in u
            assert "email" in u
            assert "created_at" in u
            # CRITICAL SECURITY CHECK: passwords and security answers must NEVER be present
            assert "password" not in u
            assert "password_hash" not in u
            assert "security_answer_hash" not in u


class TestOTPTokenTracking:
    def test_otp_lifecycle_and_single_use(self, temp_db):
        token_id = "tok_test_123"
        email = "reset@infosys.com"
        raw_otp = "849201"
        otp_hash = hash_password(raw_otp)
        expires_at = time.time() + 300  # 5 minutes ahead

        store_otp_record(token_id, email, otp_hash, expires_at, db_path=temp_db)

        # 1. Correct verification
        ok, msg = verify_and_consume_otp_record(
            token_id=token_id,
            input_otp=raw_otp,
            check_otp_fn=verify_password,
            db_path=temp_db
        )
        assert ok is True
        assert "verified successfully" in msg.lower()

        # 2. Replay / reuse attempt must be rejected
        ok_reuse, msg_reuse = verify_and_consume_otp_record(
            token_id=token_id,
            input_otp=raw_otp,
            check_otp_fn=verify_password,
            db_path=temp_db
        )
        assert ok_reuse is False
        assert "already been used" in msg_reuse.lower()

    def test_expired_otp_rejection(self, temp_db):
        token_id = "tok_expired"
        email = "expired@infosys.com"
        raw_otp = "123456"
        otp_hash = hash_password(raw_otp)
        expires_at = time.time() - 10  # Expired 10 seconds ago

        store_otp_record(token_id, email, otp_hash, expires_at, db_path=temp_db)

        ok, msg = verify_and_consume_otp_record(
            token_id=token_id,
            input_otp=raw_otp,
            check_otp_fn=verify_password,
            db_path=temp_db
        )
        assert ok is False
        assert "expired" in msg.lower()

    def test_incorrect_otp_attempt_limits(self, temp_db):
        token_id = "tok_wrong"
        email = "wrong@infosys.com"
        raw_otp = "999888"
        otp_hash = hash_password(raw_otp)
        expires_at = time.time() + 300

        store_otp_record(token_id, email, otp_hash, expires_at, db_path=temp_db)

        # Test failed attempts
        for attempt in range(1, 6):
            ok, msg = verify_and_consume_otp_record(
                token_id=token_id,
                input_otp="000000",
                check_otp_fn=verify_password,
                max_attempts=5,
                db_path=temp_db
            )
            assert ok is False

        # 6th attempt should hit maximum attempts limit
        ok_6, msg_6 = verify_and_consume_otp_record(
            token_id=token_id,
            input_otp=raw_otp,  # Even with correct OTP now, should be locked out
            check_otp_fn=verify_password,
            max_attempts=5,
            db_path=temp_db
        )
        assert ok_6 is False
        assert "maximum" in msg_6.lower()
