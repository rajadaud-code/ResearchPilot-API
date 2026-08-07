"""
User Pydantic Schemas for Validation and Serialization.

===============================================================================
EXPRESS / ZOD VS. PYDANTIC V2 SCHEMAS
===============================================================================
In Node.js / Express:
  - Input validation is done via `zod.object({ email: zod.string().email() })`.
  - Output serialization is done manually by deleting `password` keys before returning `res.json(user)`.

In FastAPI / Pydantic v2:
  - `UserCreate` validates HTTP request body inputs (checking email formatting, minimum password length).
  - `UserResponse` uses `model_config = ConfigDict(from_attributes=True)` to convert SQLAlchemy ORM instances
    into JSON responses automatically, safely omitting internal secrets like `hashed_password`.
===============================================================================
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserBase(BaseModel):
    """Base user properties shared across create and read schemas."""
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration request body."""
    password: str = Field(..., min_length=6, description="User password (min 6 chars)")


class UserResponse(UserBase):
    """Schema for returning user details in API responses (hides hashed_password)."""
    id: int
    is_active: bool
    created_at: datetime

    # Pydantic v2 configuration enabling ORM mode (serialization directly from SQLAlchemy models)
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Schema for JWT access token responses."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded JWT token payload claims."""
    email: Optional[str] = None
