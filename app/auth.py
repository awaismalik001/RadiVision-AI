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

def validate_password_complexity(password: str) -> Tuple[bool, str]:
    """Ensures password meets minimum security criteria: >= 8 characters, letters & numbers."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one alphabetical letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one numeric digit."
    return True, "Password is secure."

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

def authenticate_user(username: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Authenticates a user against the SQLite database.
    Returns (success, message, user_dict).
    """
    from app.database import db
    
    username = username.strip()
    user = db.get_user_by_username(username)
    
    # Generic error message to prevent account enumeration
    generic_error = "Invalid username or password."

    if not user:
        db.log_activity(None, username, "FAILED_LOGIN", "Attempt with non-existent username.")
        return False, generic_error, None

    if not user.get("is_active", 1):
        db.log_activity(user["user_id"], username, "FAILED_LOGIN", "Attempt on deactivated account.")
        return False, "This account has been deactivated. Please contact an Administrator.", None

    if not verify_password(password, user["password_hash"]):
        db.log_activity(user["user_id"], username, "FAILED_LOGIN", "Incorrect password provided.")
        return False, generic_error, None

    # Login successful
    SessionManager.set_user(user)
    db.log_activity(user["user_id"], username, "SUCCESSFUL_LOGIN", f"Role: {user['role']}")
    return True, "Authentication successful.", user
