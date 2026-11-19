"""Security & Authentication Utilities for AgroAI.

Provides NIST-compliant password hashing and verification using hashlib.pbkdf2_hmac
(SHA256, 100,000 rounds, random 16-byte hex salt).
Zero external C-dependency risk, guaranteed cross-platform reliability.
"""

import os
import hmac
import hashlib
import secrets
from typing import Optional
from fastapi import Header, HTTPException, Depends, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db

HASH_ALGORITHM = "sha256"
ITERATIONS = 100_000
SALT_SIZE = 16

def hash_password(password: str) -> str:
    """Hash a plaintext password using PBKDF2-HMAC-SHA256 with a unique random salt."""
    if not password:
        raise ValueError("Password cannot be empty")
    salt = secrets.token_hex(SALT_SIZE)
    key = hashlib.pbkdf2_hmac(
        HASH_ALGORITHM,
        password.encode("utf-8"),
        salt.encode("utf-8"),
        ITERATIONS
    )
    return f"pbkdf2:{HASH_ALGORITHM}:{ITERATIONS}${salt}${key.hex()}"

def verify_password(password: str, password_hash: str) -> bool:
    """Securely verify a plaintext password against a stored PBKDF2 hash."""
    if not password or not password_hash:
        return False
    try:
        scheme, salt, stored_key = password_hash.split("$")
        algo_part, iter_part = scheme.split(":")[-2], scheme.split(":")[-1]
        iterations = int(iter_part)
        
        computed_key = hashlib.pbkdf2_hmac(
            algo_part,
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations
        ).hex()
        
        return secrets.compare_digest(computed_key, stored_key)
    except Exception:
        return False

def generate_session_token() -> str:
    """Generate a high-entropy URL-safe cryptographic session token."""
    return secrets.token_urlsafe(32)

def extract_token(
    authorization: Optional[str] = Header(None),
    x_auth_token: Optional[str] = Header(None)
) -> Optional[str]:
    """Extract bearer token from Authorization header or X-Auth-Token."""
    if authorization and authorization.startswith("Bearer "):
        return authorization.split("Bearer ", 1)[1].strip()
    if x_auth_token:
        return x_auth_token.strip()
    return None

def get_optional_current_user(
    token: Optional[str] = Depends(extract_token),
    db: Session = Depends(get_db)
):
    """Retrieve the currently authenticated User if a valid session token is provided."""
    if not token:
        return None
    from backend.app.services.auth_service import AuthService
    return AuthService.get_user_by_token(db, token)

def get_current_user(
    user = Depends(get_optional_current_user)
):
    """Require an authenticated User; raise HTTP 401 if unauthenticated."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in to access this resource.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
