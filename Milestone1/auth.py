"""
Authentication, validation, hashing, and JWT session handling module for Milestone 1.

Strictly enforces Milestone 1 requirements:
- Mandatory field validations
- Email format rule (>=2 chars before @, >=2 chars between @ and dot, >=2 chars after dot)
- Password complexity rules (>=8 chars, uppercase, lowercase, digit, special symbol)
- bcrypt salted hashing for passwords and normalized security answers
- JWT session token generation, verification, and expiration handling
"""

import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

import bcrypt
import jwt

try:
    from Milestone1.config import get_jwt_secret
except ImportError:
    from config import get_jwt_secret

# Special symbols regex for password rule
SPECIAL_SYMBOLS_PATTERN = r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\/`~;']"


# ── Field & Format Validations ──────────────────────────────────────────

def validate_mandatory_fields(**fields: Any) -> Tuple[bool, str]:
    """
    Ensure no required field is empty or whitespace-only.
    Returns (True, "") or (False, "Field '<name>' cannot be empty.")
    """
    for name, value in fields.items():
        if value is None or (isinstance(value, str) and value.strip() == ""):
            formatted_name = name.replace("_", " ").capitalize()
            return False, f"The field '{formatted_name}' is mandatory and cannot be empty."
    return True, ""


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email address according to Milestone 1 Step 8:
    'At least 2 letters before the @, at least 2 letters between the @ and the dot,
    and at least 2 letters after the final dot — e.g. an address shaped like ab@cd.ef.'
    """
    if not email or not isinstance(email, str):
        return False, "Email address is required."

    clean_email = email.strip()

    # Must contain exactly one '@'
    if clean_email.count("@") != 1:
        return False, "Email must contain exactly one '@' symbol."

    local_part, domain_part = clean_email.split("@")

    # At least 2 characters before the @
    if len(local_part) < 2:
        return False, "Email must contain at least 2 characters before the '@' (e.g. 'ab@cd.ef')."

    # Domain part must have at least one dot
    if "." not in domain_part:
        return False, "Email domain must contain a dot (e.g. 'ab@cd.ef')."

    domain_segments = domain_part.rsplit(".", 1)
    before_last_dot = domain_segments[0]
    after_last_dot = domain_segments[1]

    # At least 2 characters between the @ and the final dot
    # If multiple dots exist, the last domain segment before the final dot (or entire prefix)
    # must have at least 2 chars.
    last_subdomain = before_last_dot.split(".")[-1]
    if len(last_subdomain) < 2 or len(before_last_dot) < 2:
        return False, "Email must contain at least 2 characters between the '@' and the dot (e.g. 'ab@cd.ef')."

    # At least 2 characters after the final dot
    if len(after_last_dot) < 2:
        return False, "Email must contain at least 2 characters after the final dot (e.g. 'ab@cd.ef')."

    # Standard RFC-like character safety regex check
    pattern = r"^[a-zA-Z0-9._%+-]{2,}@[a-zA-Z0-9.-]{2,}\.[a-zA-Z]{2,}$"
    if not re.match(pattern, clean_email):
        return False, "Email contains invalid characters or does not meet the format requirements."

    return True, ""


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password complexity according to Milestone 1 Step 8:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special symbol
    """
    if not password or not isinstance(password, str):
        return False, "Password is required."

    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."

    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number."

    if not re.search(SPECIAL_SYMBOLS_PATTERN, password):
        return False, "Password must contain at least one special symbol (e.g. @, #, $, %, !)."

    return True, ""


def validate_password_confirmation(password: str, confirm_password: str) -> Tuple[bool, str]:
    """Ensure password and confirm_password match exactly."""
    if password != confirm_password:
        return False, "Passwords do not match. Please re-enter your confirm password."
    return True, ""


# ── Password & Security Answer Hashing ──────────────────────────────────

def hash_password(password: str) -> str:
    """Hash password using bcrypt with a unique salt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against a bcrypt hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def normalize_security_answer(answer: str) -> str:
    """Normalize security answer by stripping whitespace and converting to lowercase."""
    if not answer:
        return ""
    # Collapse multiple internal spaces and trim
    return " ".join(answer.strip().lower().split())


def hash_security_answer(answer: str) -> str:
    """Hash normalized security answer using bcrypt."""
    normalized = normalize_security_answer(answer)
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(normalized.encode("utf-8"), salt).decode("utf-8")


def verify_security_answer(plain_answer: str, hashed_answer: str) -> bool:
    """Verify plain security answer against stored bcrypt hash after normalization."""
    if not plain_answer or not hashed_answer:
        return False
    normalized = normalize_security_answer(plain_answer)
    try:
        return bcrypt.checkpw(
            normalized.encode("utf-8"),
            hashed_answer.encode("utf-8")
        )
    except Exception:
        return False


# ── JWT Session Management ──────────────────────────────────────────────

def create_session_jwt(
    username: str,
    email: str,
    role: str = "user",
    expires_in_hours: int = 2
) -> str:
    """
    Issue a signed JWT session token upon successful login (Step 7).
    """
    secret = get_jwt_secret()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "username": username,
        "email": email,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=expires_in_hours)).timestamp())
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def verify_session_jwt(token: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Verify and decode a session JWT token.
    Returns (is_valid, payload, error_message).
    """
    if not token or not isinstance(token, str):
        return False, None, "Session token is missing."

    secret = get_jwt_secret()
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        if "username" not in payload or "email" not in payload:
            return False, None, "Session token payload is invalid."
        return True, payload, "Token is valid."
    except jwt.ExpiredSignatureError:
        return False, None, "Session expired. Please log in again."
    except jwt.InvalidTokenError:
        return False, None, "Invalid session token. Please log in again."
    except Exception as e:
        return False, None, f"Token verification error: {str(e)}"
