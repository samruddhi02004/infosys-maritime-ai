"""
Unified SQLite database module for Milestone 1.

Provides a unified, thread-safe schema for signup, login,
security-question recovery, OTP verification tracking, and admin user listing.
"""

import os
import sqlite3
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

try:
    from Milestone1.config import DEFAULT_DB_FILENAME
except ImportError:
    from config import DEFAULT_DB_FILENAME

# Predefined fixed list of security questions as required by Step 3
SECURITY_QUESTIONS: List[str] = [
    "What was the name of your first elementary school?",
    "What is the name of your favorite childhood pet?",
    "In which city or town was your first job?",
    "What is your mother's maiden name?",
    "What was your childhood nickname?"
]


def resolve_db_path(db_path: Optional[str] = None) -> str:
    """Resolve the SQLite database path, defaulting to users.db in the Milestone1 folder."""
    if db_path:
        return db_path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, DEFAULT_DB_FILENAME)


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Create a thread-safe connection with row_factory configured."""
    path = resolve_db_path(db_path)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize the unified database tables and indexes."""
    conn = get_connection(db_path)
    try:
        with conn:
            # 1. Main Users Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL COLLATE NOCASE,
                    email TEXT UNIQUE NOT NULL COLLATE NOCASE,
                    password_hash TEXT NOT NULL,
                    security_question TEXT NOT NULL,
                    security_answer_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
            """)

            # 2. OTP Tracking Table to enforce 5-minute expiry, single-use, and attempt limits
            conn.execute("""
                CREATE TABLE IF NOT EXISTS otp_tokens (
                    token_id TEXT PRIMARY KEY,
                    email TEXT NOT NULL COLLATE NOCASE,
                    otp_hash TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL,
                    is_used INTEGER DEFAULT 0,
                    attempts INTEGER DEFAULT 0
                );
            """)

            # Indexes for fast lookup
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_otp_email ON otp_tokens(email);")
    finally:
        conn.close()


def check_username_exists(username: str, db_path: Optional[str] = None) -> bool:
    """Check if a username is already taken."""
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT 1 FROM users WHERE username = ?", (username.strip(),)).fetchone()
        return row is not None
    finally:
        conn.close()


def check_email_exists(email: str, db_path: Optional[str] = None) -> bool:
    """Check if an email is already registered."""
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT 1 FROM users WHERE email = ?", (email.strip().lower(),)).fetchone()
        return row is not None
    finally:
        conn.close()


def create_user(
    username: str,
    email: str,
    password_hash: str,
    security_question: str,
    security_answer_hash: str,
    db_path: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Register a new user in the unified database.
    Explicitly checks for duplicate username or email to give actionable feedback.
    """
    clean_username = username.strip()
    clean_email = email.strip().lower()

    if check_username_exists(clean_username, db_path=db_path):
        return False, f"Username '{clean_username}' is already taken. Please choose another username."

    if check_email_exists(clean_email, db_path=db_path):
        return False, f"Email '{clean_email}' is already registered. Please sign in or reset your password."

    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO users (username, email, password_hash, security_question, security_answer_hash, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (clean_username, clean_email, password_hash, security_question, security_answer_hash, created_at)
            )
        return True, "User registered successfully."
    except sqlite3.IntegrityError as e:
        err_msg = str(e).lower()
        if "username" in err_msg:
            return False, f"Username '{clean_username}' is already taken."
        elif "email" in err_msg:
            return False, f"Email '{clean_email}' is already registered."
        return False, "Registration failed due to a database integrity error."
    finally:
        conn.close()


def get_user_by_identifier(identifier: str, db_path: Optional[str] = None) -> Optional[Dict]:
    """
    Retrieve user record by either username OR email address.
    Enables unified login using username or email.
    """
    clean_id = identifier.strip()
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            """
            SELECT id, username, email, password_hash, security_question, security_answer_hash, created_at
            FROM users
            WHERE username = ? OR email = ?
            """,
            (clean_id, clean_id.lower())
        ).fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def get_user_by_username(username: str, db_path: Optional[str] = None) -> Optional[Dict]:
    """Retrieve user record specifically by username."""
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            """
            SELECT id, username, email, password_hash, security_question, security_answer_hash, created_at
            FROM users
            WHERE username = ?
            """,
            (username.strip(),)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_email(email: str, db_path: Optional[str] = None) -> Optional[Dict]:
    """Retrieve user record specifically by email."""
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            """
            SELECT id, username, email, password_hash, security_question, security_answer_hash, created_at
            FROM users
            WHERE email = ?
            """,
            (email.strip().lower(),)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_password(identifier: str, new_password_hash: str, db_path: Optional[str] = None) -> bool:
    """Update password hash for a user by username or email."""
    clean_id = identifier.strip()
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                """
                UPDATE users
                SET password_hash = ?
                WHERE username = ? OR email = ?
                """,
                (new_password_hash, clean_id, clean_id.lower())
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def get_all_registered_users(db_path: Optional[str] = None) -> List[Dict]:
    """
    Fetch list of all registered users for the Admin Dashboard.
    CRITICAL: Never selects or exposes password_hash or security_answer_hash.
    """
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT id, username, email, created_at
            FROM users
            ORDER BY id ASC
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ── OTP Tracking and Single-Use Enforcement ────────────────────────────

def store_otp_record(
    token_id: str,
    email: str,
    otp_hash: str,
    expires_at: float,
    db_path: Optional[str] = None
) -> None:
    """Store an active OTP record with expiration and usage tracking."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO otp_tokens (token_id, email, otp_hash, created_at, expires_at, is_used, attempts)
                VALUES (?, ?, ?, ?, ?, 0, 0)
                """,
                (token_id, email.strip().lower(), otp_hash, time.time(), expires_at)
            )
    finally:
        conn.close()


def verify_and_consume_otp_record(
    token_id: str,
    input_otp: str,
    check_otp_fn,
    max_attempts: int = 5,
    db_path: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Verify OTP with single-use consumption and brute-force attempt limits.
    Prevents replay attacks, repeated guesses, and expired OTP usage.
    """
    now = time.time()
    conn = get_connection(db_path)
    try:
        with conn:
            row = conn.execute(
                "SELECT email, otp_hash, expires_at, is_used, attempts FROM otp_tokens WHERE token_id = ?",
                (token_id,)
            ).fetchone()

            if not row:
                return False, "Invalid or non-existent verification session. Please request a new OTP."

            if row["is_used"] == 1:
                return False, "This OTP has already been used. Please request a fresh code."

            if now > row["expires_at"]:
                return False, "This verification code has expired (valid for 5 minutes). Please request a new one."

            if row["attempts"] >= max_attempts:
                return False, "Maximum verification attempts exceeded for this code. Please request a new OTP."

            # Verify the OTP hash using the provided checker function
            if check_otp_fn(input_otp, row["otp_hash"]):
                # Mark as consumed immediately
                conn.execute(
                    "UPDATE otp_tokens SET is_used = 1 WHERE token_id = ?",
                    (token_id,)
                )
                return True, "OTP verified successfully."
            else:
                # Increment failed attempts
                new_attempts = row["attempts"] + 1
                conn.execute(
                    "UPDATE otp_tokens SET attempts = ? WHERE token_id = ?",
                    (new_attempts, token_id)
                )
                remaining = max_attempts - new_attempts
                if remaining > 0:
                    return False, f"Incorrect verification code. {remaining} attempt(s) remaining."
                return False, "Maximum attempts exceeded. This OTP has been invalidated."
    finally:
        conn.close()
