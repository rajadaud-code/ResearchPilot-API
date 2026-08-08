"""
Core Security & Authentication Utilities.

===============================================================================
EXPRESS / NODE.JS VS. FASTAPI SECURITY ARCHITECTURE
===============================================================================
In Node.js / Express:
  - Password hashing uses `bcrypt.hash(password, 10)` or `argon2`.
  - JWT creation uses `jwt.sign(payload, secret, { expiresIn: '1h' })`.
  - Token verification uses `jwt.verify(token, secret)` in custom middleware.

In FastAPI / Python:
  - Password hashing uses `passlib.context.CryptContext` with `bcrypt`.
  - JWT creation and validation use `jose` (`python-jose`) or `PyJWT`.
  - Tokens are signed with `SECRET_KEY` using HMAC-SHA256 (`HS256`) algorithm.
  - Expiration claims (`exp`) and subject claims (`sub`) follow RFC 7519 standards.
===============================================================================
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# JWT Secret, Algorithm, and Default Expiration duration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Password Hashing Context using bcrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against an existing bcrypt hash.
    
    Args:
        plain_password (str): Password supplied during login.
        hashed_password (str): Stored bcrypt hash from database.

    Returns:
        bool: True if password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hashes a plain-text password using salted bcrypt algorithm.
    
    Args:
        password (str): Raw user password.

    Returns:
        str: Salted bcrypt hash string for database storage.
    """
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a signed JWT Access Token containing user claim payload.
    
    Args:
        data (Dict[str, Any]): Claims to encode in payload (e.g. {"sub": user.email}).
        expires_delta (Optional[timedelta]): Custom token expiration duration.

    Returns:
        str: Encoded and signed JWT string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Standard JWT Expiration claim
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodes and verifies a JWT access token signature using settings.SECRET_KEY.
    
    Args:
        token (str): Incoming JWT bearer token string.

    Returns:
        Optional[Dict[str, Any]]: Decoded claims payload if valid, None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
