"""
Automated unit tests for OTP generation, JWT OTP token lifecycle,
expiry enforcement, attempt limiting, and mocked email delivery.
"""

import os
import smtplib
import tempfile
import time
from unittest.mock import MagicMock, patch
import pytest

from Milestone1.database import init_db
from Milestone1.otp_service import (
    create_otp_session,
    generate_otp,
    send_otp_email,
    verify_otp_session,
)


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(db_path=path)
    yield path
    try:
        os.remove(path)
    except OSError:
        pass


class TestOTPService:
    def test_generate_otp_cryptographic_properties(self):
        """Test that generated OTPs are 6-digit strings and within expected range."""
        generated_set = set()
        for _ in range(100):
            otp = generate_otp()
            assert isinstance(otp, str)
            assert len(otp) == 6
            assert otp.isdigit()
            assert 100000 <= int(otp) <= 999999
            generated_set.add(otp)
        # Verify randomness / variability across 100 runs
        assert len(generated_set) > 90

    def test_otp_session_success_and_single_use(self, temp_db):
        """Test successful verification and single-use enforcement (replay prevention)."""
        email = "student@infosys.com"
        otp = "739102"
        jwt_token, token_id = create_otp_session(email, otp, db_path=temp_db)

        assert isinstance(jwt_token, str)
        assert len(jwt_token) > 20

        # Successful verification
        ok, msg = verify_otp_session(jwt_token, otp, email, db_path=temp_db)
        assert ok is True
        assert "verified successfully" in msg.lower()

        # Immediate replay / reuse must fail
        ok_reuse, msg_reuse = verify_otp_session(jwt_token, otp, email, db_path=temp_db)
        assert ok_reuse is False
        assert "already been used" in msg_reuse.lower()

    def test_otp_session_wrong_otp(self, temp_db):
        """Test rejection of incorrect verification code."""
        email = "student@infosys.com"
        otp = "739102"
        jwt_token, _ = create_otp_session(email, otp, db_path=temp_db)

        ok, msg = verify_otp_session(jwt_token, "000000", email, db_path=temp_db)
        assert ok is False
        assert "incorrect verification code" in msg.lower()

    def test_otp_session_email_mismatch(self, temp_db):
        """Test that verification token cannot be used for a different email."""
        email = "student@infosys.com"
        otp = "739102"
        jwt_token, _ = create_otp_session(email, otp, db_path=temp_db)

        ok, msg = verify_otp_session(jwt_token, otp, "other@infosys.com", db_path=temp_db)
        assert ok is False
        assert "mismatch" in msg.lower()

    def test_otp_expiry_enforcement(self, temp_db):
        """Test that expired OTPs are strictly rejected."""
        email = "student@infosys.com"
        otp = "543210"

        # Create session
        jwt_token, token_id = create_otp_session(email, otp, db_path=temp_db)

        # Manually backdate the expires_at timestamp in SQLite database to simulate expiry
        from Milestone1.database import get_connection
        conn = get_connection(db_path=temp_db)
        with conn:
            conn.execute("UPDATE otp_tokens SET expires_at = ? WHERE token_id = ?", (time.time() - 60, token_id))
        conn.close()

        ok, msg = verify_otp_session(jwt_token, otp, email, db_path=temp_db)
        assert ok is False
        assert "expired" in msg.lower()

    def test_otp_brute_force_attempt_limits(self, temp_db):
        """Test that multiple incorrect attempts lock out the verification session."""
        email = "student@infosys.com"
        otp = "889900"
        jwt_token, token_id = create_otp_session(email, otp, db_path=temp_db)

        # 5 incorrect attempts
        for attempt in range(1, 6):
            ok, msg = verify_otp_session(jwt_token, "111111", email, db_path=temp_db)
            assert ok is False

        # 6th attempt with the CORRECT code must now be rejected due to lockout
        ok_locked, msg_locked = verify_otp_session(jwt_token, otp, email, db_path=temp_db)
        assert ok_locked is False
        assert "maximum" in msg_locked.lower() or "invalidated" in msg_locked.lower()

    # ── Mocked SMTP Delivery Tests (Zero Real Emails Sent) ───────────────

    def test_send_email_graceful_missing_credentials(self):
        """Test graceful error message when EMAIL_ADDRESS or EMAIL_PASSWORD is missing."""
        with patch("Milestone1.otp_service.get_email_address", return_value=None), \
             patch("Milestone1.otp_service.get_email_password", return_value=None):
            ok, msg = send_otp_email("recipient@example.com", "123456")
            assert ok is False
            assert "credentials are not configured" in msg
            assert "EMAIL_ADDRESS" in msg
            assert "EMAIL_PASSWORD" in msg

    def test_mocked_smtp_email_delivery_success(self):
        """Verify that email delivery connects to smtp.gmail.com:587, starts TLS, authenticates, and dispatches."""
        mock_server = MagicMock()

        with patch("Milestone1.otp_service.get_email_address", return_value="test.sender@gmail.com"), \
             patch("Milestone1.otp_service.get_email_password", return_value="dummy_app_password_16char"), \
             patch("smtplib.SMTP", return_value=mock_server) as mock_smtp_class:

            ok, msg = send_otp_email("student@infosys.com", "987654")

            assert ok is True
            assert "sent successfully" in msg.lower()

            # Verify SMTP interactions
            mock_smtp_class.assert_called_once_with("smtp.gmail.com", 587, timeout=15)
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with("test.sender@gmail.com", "dummy_app_password_16char")
            mock_server.sendmail.assert_called_once()

            # Verify sendmail arguments
            args, kwargs = mock_server.sendmail.call_args
            assert args[0] == "test.sender@gmail.com"
            assert args[1] == "student@infosys.com"
            raw_message_text = args[2]
            assert "987654" in raw_message_text
            assert "Infosys Portal - Password Reset Verification Code" in raw_message_text

            mock_server.quit.assert_called_once()

    def test_mocked_smtp_auth_failure(self):
        """Test handling of SMTPAuthenticationError without crashing or exposing secrets."""
        mock_server = MagicMock()
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b"5.7.8 Username and Password not accepted")

        with patch("Milestone1.otp_service.get_email_address", return_value="test.sender@gmail.com"), \
             patch("Milestone1.otp_service.get_email_password", return_value="wrong_app_password"), \
             patch("smtplib.SMTP", return_value=mock_server):

            ok, msg = send_otp_email("student@infosys.com", "987654")

            assert ok is False
            assert "Authentication failed" in msg
            # Password must NOT be leaked in error message
            assert "wrong_app_password" not in msg

    def test_mocked_smtp_network_error(self):
        """Test handling of network/timeout connection errors."""
        with patch("Milestone1.otp_service.get_email_address", return_value="test.sender@gmail.com"), \
             patch("Milestone1.otp_service.get_email_password", return_value="valid_password"), \
             patch("smtplib.SMTP", side_effect=OSError("Network unreachable")):

            ok, msg = send_otp_email("student@infosys.com", "987654")

            assert ok is False
            assert "Failed to send email" in msg
