"""
OTP generation, JWT verification, and email dispatch service for Milestone 1.

Features:
- Cryptographically secure 6-digit OTP generation using secrets module
- Signed 5-minute JWT verification token
- Single-use consumption and attempt limiting via unified SQLite database
- Gmail SMTP delivery using TLS and anti-spam RFC headers
- Safe secret lookup from Colab Secrets without exposing credentials
"""

import datetime
import secrets
import smtplib
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
from typing import Optional, Tuple

import jwt

try:
    from Milestone1.auth import hash_password, verify_password
    from Milestone1.config import (
        OTP_EXPIRY_MINUTES,
        get_email_address,
        get_email_password,
        get_jwt_secret,
    )
    from Milestone1.database import store_otp_record, verify_and_consume_otp_record
except ImportError:
    from auth import hash_password, verify_password
    from config import (
        OTP_EXPIRY_MINUTES,
        get_email_address,
        get_email_password,
        get_jwt_secret,
    )
    from database import store_otp_record, verify_and_consume_otp_record



def generate_otp() -> str:
    """Generate an unbiased, cryptographically secure 6-digit numerical OTP."""
    return f"{secrets.randbelow(900000) + 100000}"


def create_otp_session(email: str, otp: str, db_path: Optional[str] = None) -> Tuple[str, str]:
    """
    Create a secure OTP session:
    1. Generates a unique session token_id.
    2. Hashes the OTP using bcrypt.
    3. Persists OTP metadata in the database for single-use consumption and attempt limits.
    4. Issues a signed JWT containing token_id and otp_hash with a 5-minute expiration.
    Returns (jwt_token, token_id).
    """
    clean_email = email.strip().lower()
    token_id = str(uuid.uuid4())
    otp_hash = hash_password(otp)
    secret = get_jwt_secret()

    now = datetime.datetime.now(datetime.timezone.utc)
    exp = now + datetime.timedelta(minutes=OTP_EXPIRY_MINUTES)
    expires_at_timestamp = exp.timestamp()

    # Persist in SQLite for single-use and attempt enforcement
    store_otp_record(
        token_id=token_id,
        email=clean_email,
        otp_hash=otp_hash,
        expires_at=expires_at_timestamp,
        db_path=db_path
    )

    payload = {
        "sub": clean_email,
        "token_id": token_id,
        "type": "password_reset_otp",
        "iat": int(now.timestamp()),
        "exp": int(expires_at_timestamp)
    }

    jwt_token = jwt.encode(payload, secret, algorithm="HS256")
    return jwt_token, token_id


def verify_otp_session(
    jwt_token: str,
    input_otp: str,
    target_email: str,
    db_path: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Verify OTP token:
    1. Validates JWT signature, expiration, and payload claims.
    2. Enforces single-use consumption and attempt counting in the database.
    Returns (is_valid, status_message).
    """
    if not jwt_token or not input_otp:
        return False, "Verification token and 6-digit OTP code are both required."

    secret = get_jwt_secret()
    clean_email = target_email.strip().lower()

    # Step 1: Decode JWT
    try:
        payload = jwt.decode(jwt_token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return False, f"This verification code expired after {OTP_EXPIRY_MINUTES} minutes. Please request a new code."
    except jwt.InvalidTokenError:
        return False, "Verification session token is invalid or corrupted. Please request a new code."
    except Exception as e:
        return False, f"Token verification error: {str(e)}"

    # Step 2: Validate payload claims
    if payload.get("sub") != clean_email or payload.get("type") != "password_reset_otp":
        return False, "Security token mismatch. Please request a new code."

    token_id = payload.get("token_id")
    if not token_id:
        return False, "Invalid verification token structure."

    # Step 3: Verify and consume against database (single-use & attempt-limited)
    return verify_and_consume_otp_record(
        token_id=token_id,
        input_otp=input_otp.strip(),
        check_otp_fn=verify_password,
        max_attempts=5,
        db_path=db_path
    )


def send_otp_email(to_email: str, otp: str) -> Tuple[bool, str]:
    """
    Send OTP verification email via Gmail SMTP using credentials from Colab Secrets.
    Returns (success, message).
    """
    sender_email = get_email_address()
    app_password = get_email_password()

    if not sender_email or not app_password:
        return False, (
            "Gmail credentials are not configured. "
            "Please add 'EMAIL_ADDRESS' and 'EMAIL_PASSWORD' to Google Colab Secrets (or environment) to send OTPs."
        )

    clean_to = to_email.strip().lower()

    # Build MIME message with anti-spam RFC headers
    msg = MIMEMultipart("alternative")
    msg["From"] = f"Infosys Portal <{sender_email}>"
    msg["To"] = clean_to
    msg["Subject"] = "Infosys Portal - Password Reset Verification Code"
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid()
    msg["Reply-To"] = sender_email

    # Plaintext fallback
    plain_text = (
        f"Infosys Portal - Password Reset Verification Code\n\n"
        f"Your one-time verification code is: {otp}\n\n"
        f"This code will expire in {OTP_EXPIRY_MINUTES} minutes.\n"
        f"If you did not request this password reset, please ignore this email.\n\n"
        f"Infosys Springboard Internship 7.0 - User Authentication Module"
    )

    # Professional HTML template matching the Light Theme (warm white, deep navy, teal)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #faf9f6;
                margin: 0;
                padding: 24px;
                color: #0f172a;
            }}
            .card {{
                max-width: 520px;
                margin: 0 auto;
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 32px;
                box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
            }}
            .header {{
                text-align: center;
                border-bottom: 1px solid #f1f5f9;
                padding-bottom: 20px;
                margin-bottom: 24px;
            }}
            .title {{
                color: #0f172a;
                font-size: 22px;
                font-weight: 700;
                margin: 0;
            }}
            .subtitle {{
                color: #0d9488;
                font-size: 13px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-top: 4px;
            }}
            .content {{
                font-size: 15px;
                line-height: 1.6;
                color: #334155;
            }}
            .otp-container {{
                text-align: center;
                margin: 28px 0;
            }}
            .otp-badge {{
                display: inline-block;
                background: #f0fdfa;
                color: #0d9488;
                border: 2px solid #0d9488;
                border-radius: 10px;
                font-size: 32px;
                font-weight: 800;
                letter-spacing: 8px;
                padding: 14px 28px;
            }}
            .expiry-note {{
                font-size: 13px;
                color: #64748b;
                text-align: center;
                margin-top: -12px;
                margin-bottom: 24px;
            }}
            .footer {{
                font-size: 12px;
                color: #94a3b8;
                border-top: 1px solid #f1f5f9;
                padding-top: 18px;
                text-align: center;
                line-height: 1.5;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">
                <div class="title">Infosys Portal</div>
                <div class="subtitle">Secure Password Recovery</div>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>We received a password reset request for your registered account (<b>{clean_to}</b>). Please enter the 6-digit verification code below to proceed:</p>
                <div class="otp-container">
                    <div class="otp-badge">{otp}</div>
                </div>
                <div class="expiry-note">⏱️ This code expires in <b>{OTP_EXPIRY_MINUTES} minutes</b> and can only be used once.</div>
                <p>If you did not request a password reset, you can safely disregard this email. Your existing password will remain secure.</p>
            </div>
            <div class="footer">
                Infosys Springboard Internship 7.0 &bull; Milestone 1: User Authentication Module<br>
                This is an automated system notification.
            </div>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, clean_to, msg.as_string())
        server.quit()
        return True, "Verification code sent successfully. Please check your email."
    except smtplib.SMTPAuthenticationError:
        return False, "SMTP Authentication failed. Please verify that your Gmail App Password and Email Address are correct."
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"
