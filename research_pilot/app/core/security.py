"""
Core Security Module.

Provides authentication and token utility functions.
In Express/Node.js, auth middleware usually parses authorization headers manually or uses `passport` / `jsonwebtoken`.
In FastAPI, security utilities work seamlessly with FastAPI's `OAuth2PasswordBearer` and `Depends()`.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Stub helper function for JWT token creation.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=60))
    to_encode.update({"exp": expire})
    # In production, use `jose` or `pyjwt` to encode using `settings.SECRET_KEY`
    return f"mock_token_for_{to_encode.get('sub', 'user')}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Stub password comparison. In production, use `passlib.context.CryptContext` with bcrypt.
    """
    return plain_password == hashed_password
