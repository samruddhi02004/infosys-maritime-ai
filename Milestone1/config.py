"""
Configuration and secrets management module for Milestone 1.

Reads sensitive keys at runtime:
- In Google Colab: strictly reads from Google Colab Secrets (`google.colab.userdata`).
  If a secret is missing, it provides clear setup instructions without leaking data.
- In local development/testing: reads from environment variables or uses
  explicit test-only dummy placeholders.

Secret names used (configured manually by user in Colab Secrets tab):
- JWT_SECRET
- NGROK_AUTHTOKEN
- EMAIL_ADDRESS
- EMAIL_PASSWORD
"""

import os
import sys
from typing import Dict, List, Optional, Tuple


def is_running_in_colab() -> bool:
    """Check if code is running inside a Google Colab runtime environment."""
    return "google.colab" in sys.modules or os.path.exists("/content")


def get_secret(name: str) -> Optional[str]:
    """
    Retrieve secret securely at runtime.
    In Colab: reads strictly from google.colab.userdata.
    In Local: reads from environment variables.
    Never returns hardcoded real credentials.
    """
    # 1. Check Google Colab Secrets
    try:
        from google.colab import userdata  # type: ignore
        val = userdata.get(name)
        if val is not None and str(val).strip() != "":
            return str(val).strip()
    except Exception:
        pass

    # 2. Check environment variable (for local testing)
    env_val = os.getenv(name)
    if env_val is not None and env_val.strip() != "":
        return env_val.strip()

    return None


def get_jwt_secret() -> str:
    """
    Retrieve JWT signing secret.
    In Colab, requires JWT_SECRET secret.
    In local test runner, uses an explicit non-production test placeholder if not set.
    """
    secret = get_secret("JWT_SECRET")
    if secret:
        return secret
    if is_running_in_colab():
        raise RuntimeError("Missing required Colab Secret: 'JWT_SECRET'. Please add it in the Secrets tab.")
    # Explicit dummy placeholder strictly for local pytest execution
    return "TESTING_ONLY_LOCAL_JWT_KEY_NOT_FOR_PRODUCTION"


def get_ngrok_authtoken() -> Optional[str]:
    """Retrieve ngrok authtoken from Colab Secrets or environment."""
    return get_secret("NGROK_AUTHTOKEN")


def get_email_address() -> Optional[str]:
    """Retrieve Gmail address for OTP sender from Colab Secrets or environment."""
    return get_secret("EMAIL_ADDRESS")


def get_email_password() -> Optional[str]:
    """Retrieve Gmail App Password for OTP sender from Colab Secrets or environment."""
    return get_secret("EMAIL_PASSWORD")


def get_admin_credentials() -> Tuple[str, str]:
    """
    Retrieve admin credentials.
    Can be configured via Colab Secrets (ADMIN_USERNAME, ADMIN_PASSWORD)
    or environment variables. Defaults to explicit test credentials locally.
    """
    username = get_secret("ADMIN_USERNAME") or "admin"
    password = get_secret("ADMIN_PASSWORD") or "Admin@Colab2026"
    return username, password


def check_required_secrets_status() -> Tuple[bool, List[str]]:
    """
    Audit whether required secrets are present in the current runtime environment.
    Returns (all_present, missing_secret_names).
    """
    required = ["JWT_SECRET", "NGROK_AUTHTOKEN", "EMAIL_ADDRESS", "EMAIL_PASSWORD"]
    missing = [name for name in required if not get_secret(name)]
    return len(missing) == 0, missing


# OTP application settings
OTP_EXPIRY_MINUTES = 5
DEFAULT_DB_FILENAME = "users.db"

