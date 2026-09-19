"""
auth.py
-------
Authentication and session management module for RadiVision AI.
Implements salted password hashing, password complexity validation, anti-enumeration
security, and role-based session states.
"""

import os
import re
import hashlib
from typing import Optional, Dict, Any, Tuple

# Graceful import of bcrypt with standard hashlib fallback
try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False

def hash_password(password: str) -> str:
    """Hashes a plaintext password using salted bcrypt (or PBKDF2 fallback)."""
    password_bytes = password.encode('utf-8')
    if HAS_BCRYPT:
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    else:
        # Fallback to PBKDF2-HMAC-SHA256
        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac('sha256', password_bytes, salt, 100000)
        return f"pbkdf2:{salt.hex()}:{key.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a stored cryptographic hash."""
    if not hashed_password or not plain_password:
        return False
    
    password_bytes = plain_password.encode('utf-8')
    
    if HAS_BCRYPT and not hashed_password.startswith("pbkdf2:"):
        try:
            return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
        except Exception:
            return False
    else:
        # PBKDF2 verification
        try:
            parts = hashed_password.split(":")
            if len(parts) != 3 or parts[0] != "pbkdf2":
                return False
            salt = bytes.fromhex(parts[1])
            expected_key = parts[2]
            key = hashlib.pbkdf2_hmac('sha256', password_bytes, salt, 100000)
            return key.hex() == expected_key
        except Exception:
            return False

import time

# Rate limiting state: username_or_ip -> list of failure timestamps
_FAILED_LOGIN_ATTEMPTS: Dict[str, List[float]] = {}
RATE_LIMIT_WINDOW_SECONDS = 300  # 5 minutes
MAX_FAILED_ATTEMPTS = 5

def is_rate_limited(identifier: str) -> Tuple[bool, int]:
    """
    Checks whether an identifier (username or IP) has exceeded failed login threshold.
    Returns (is_limited, remaining_seconds).
    """
    now = time.time()
    attempts = _FAILED_LOGIN_ATTEMPTS.get(identifier, [])
    # Filter attempts within the sliding window
    valid_attempts = [t for t in attempts if now - t < RATE_LIMIT_WINDOW_SECONDS]
    _FAILED_LOGIN_ATTEMPTS[identifier] = valid_attempts

    if len(valid_attempts) >= MAX_FAILED_ATTEMPTS:
        earliest = valid_attempts[0]
        remaining = int(RATE_LIMIT_WINDOW_SECONDS - (now - earliest))
        return True, max(1, remaining)
    return False, 0

def record_failed_attempt(identifier: str):
    """Records a failed login attempt for rate limiting."""
    now = time.time()
    if identifier not in _FAILED_LOGIN_ATTEMPTS:
        _FAILED_LOGIN_ATTEMPTS[identifier] = []
    _FAILED_LOGIN_ATTEMPTS[identifier].append(now)

def clear_failed_attempts(identifier: str):
    """Clears failed attempts upon successful login."""
    if identifier in _FAILED_LOGIN_ATTEMPTS:
        del _FAILED_LOGIN_ATTEMPTS[identifier]

def validate_password_complexity(password: str) -> Tuple[bool, str]:
    """
    Enforces strict hospital-grade password protocols:
    >= 8 characters, at least 1 uppercase letter, 1 lowercase letter, 1 digit, and 1 special symbol.
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter (A-Z)."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter (a-z)."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one numeric digit (0-9)."
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        return False, "Password must contain at least one special character (!@#$%^&* etc.)."
    return True, "Password meets clinical security standards."

def validate_email(email: str) -> bool:
    """Validates email format."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email.strip()))

class SessionManager:
    """Manages global logged-in session state."""
    _current_user: Optional[Dict[str, Any]] = None

    @classmethod
    def set_user(cls, user: Dict[str, Any]):
        cls._current_user = user

    @classmethod
    def get_user(cls) -> Optional[Dict[str, Any]]:
        return cls._current_user

    @classmethod
    def get_user_id(cls) -> Optional[int]:
        return cls._current_user.get("user_id") if cls._current_user else None

    @classmethod
    def get_username(cls) -> str:
        return cls._current_user.get("username", "Guest") if cls._current_user else "Guest"

    @classmethod
    def get_role(cls) -> str:
        return cls._current_user.get("role", "User") if cls._current_user else "User"

    @classmethod
    def is_admin(cls) -> bool:
        return cls.get_role() == "Admin"

    @classmethod
    def logout(cls):
        cls._current_user = None

def authenticate_user(username: str, password: str, client_ip: str = "127.0.0.1") -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Authenticates a user against the SQLite database with anti-brute-force rate-limiting.
    Returns (success, message, user_dict).
    """
    from app.database import db

    username = username.strip()
    rate_key = f"{username}_{client_ip}"

    # Check rate limiting
    limited, seconds_left = is_rate_limited(rate_key)
    if limited:
        return False, f"Access blocked: Too many failed login attempts. Please wait {seconds_left} seconds before trying again.", None

    user = db.get_user_by_username(username)
    generic_error = "Invalid username or password."

    if not user:
        record_failed_attempt(rate_key)
        db.log_activity(None, username, "FAILED_LOGIN", f"Attempt with non-existent username from {client_ip}.")
        return False, generic_error, None

    if not user.get("is_active", 1):
        db.log_activity(user["user_id"], username, "FAILED_LOGIN", "Attempt on deactivated account.")
        return False, "This account has been deactivated. Please contact a System Administrator.", None

    if not verify_password(password, user["password_hash"]):
        record_failed_attempt(rate_key)
        db.log_activity(user["user_id"], username, "FAILED_LOGIN", f"Incorrect password provided from {client_ip}.")
        return False, generic_error, None

    # Login successful - reset rate limit counter
    clear_failed_attempts(rate_key)
    safe_user = {
        "user_id": user["user_id"],
        "full_name": user["full_name"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "phone": user.get("phone", ""),
        "country": user.get("country") or "Pakistan",
        "city": user.get("city") or "Rawalpindi",
        "is_active": user["is_active"]
    }
    SessionManager.set_user(safe_user)
    db.log_activity(user["user_id"], username, "SUCCESSFUL_LOGIN", f"Role: {user['role']}")
    return True, "Authentication successful.", safe_user

def admin_update_credentials(
    current_user: Dict[str, Any],
    target_user_id: int,
    new_username: Optional[str] = None,
    new_password: Optional[str] = None,
    new_full_name: Optional[str] = None,
    new_email: Optional[str] = None,
    new_role: Optional[str] = None,
    new_is_active: Optional[bool] = None
) -> Tuple[bool, str]:
    """
    Enforces Phase 4 security rule: ONLY administrators are authorized to update
    user credentials (usernames, passwords, and permissions).
    """
    from app.database import db

    # 1. Strict Administrator Authorization Check
    if not current_user or current_user.get("role") != "Admin":
        return False, "Access Denied: Credential updates are strictly restricted to System Administrators."

    target_user = db.get_user_by_id(target_user_id)
    if not target_user:
        return False, f"Target user ID #{target_user_id} does not exist."

    # 2. If updating username, check uniqueness
    if new_username and new_username.strip() != target_user["username"]:
        existing = db.get_user_by_username(new_username.strip())
        if existing and existing["user_id"] != target_user_id:
            return False, f"Username '{new_username}' is already in use by another account."

    # 3. If updating password, enforce clinical complexity
    hashed_pw = None
    if new_password:
        valid_pw, pw_msg = validate_password_complexity(new_password)
        if not valid_pw:
            return False, pw_msg
        hashed_pw = hash_password(new_password)

    # 4. Commit updates to SQLite
    db.update_user_credentials(
        user_id=target_user_id,
        username=new_username.strip() if new_username else None,
        full_name=new_full_name.strip() if new_full_name else None,
        email=new_email.strip() if new_email else None,
        password_hash=hashed_pw,
        role=new_role if new_role in ("Admin", "User") else None,
        is_active=new_is_active
    )

    admin_name = current_user.get("username", "Admin")
    db.log_activity(
        current_user.get("user_id"),
        admin_name,
        "CREDENTIAL_UPDATE",
        f"Admin updated credentials for user ID #{target_user_id} ({target_user['username']})."
    )

    return True, f"Credentials for user #{target_user_id} updated successfully by Administrator."

def admin_delete_user(current_user: Dict[str, Any], target_user_id: int) -> Tuple[bool, str]:
    """
    Deletes a user or admin account with strict protection for master administrator 'awaismalik001'.
    """
    from app.database import db

    if not current_user or current_user.get("role") != "Admin":
        return False, "Access Denied: Account deletion is strictly restricted to System Administrators."

    target_user = db.get_user_by_id(target_user_id)
    if not target_user:
        return False, f"Target user ID #{target_user_id} does not exist."

    target_username = (target_user.get("username") or "").strip().lower()
    if target_username == "awaismalik001":
        return False, "Security Violation: Master Administrator 'awaismalik001' is permanently protected and cannot be deleted under any circumstances."

    curr_user_id = current_user.get("user_id")
    curr_username = (current_user.get("username") or "").strip().lower()
    if (curr_user_id is not None and int(curr_user_id) == int(target_user_id)) or (curr_username and curr_username == target_username):
        return False, "Action Disallowed: You cannot delete your own active administrative session."

    ok, msg = db.delete_user(target_user_id)
    if ok:
        admin_name = current_user.get("username", "Admin")
        db.log_activity(
            current_user.get("user_id"),
            admin_name,
            "USER_DELETED",
            f"Admin '{admin_name}' deleted {target_user.get('role')} account '{target_username}' (ID #{target_user_id})."
        )

    return ok, msg

