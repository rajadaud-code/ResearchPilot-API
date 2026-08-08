"""
Authentication & User Management API Routes.

===============================================================================
EXPRESS / NODE.JS VS. FASTAPI AUTHENTICATION ENDPOINTS
===============================================================================
In Node.js / Express:
  - User registration reads `req.body`, checks DB, hashes password with bcrypt, inserts record, returns JSON.
  - Login route verifies password, signs JWT, returns `{ token }`.

In FastAPI / Python:
  - Input bodies are validated automatically against Pydantic schemas (`UserCreate`).
  - Passlib hashes passwords securely before persisting to PostgreSQL via SQLAlchemy `AsyncSession`.
  - Supports both standard OAuth2 form login (`OAuth2PasswordRequestForm`) for Swagger UI interactivity
    and standard JSON body authentication.
===============================================================================
"""

from typing import Union
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_user
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserResponse, Token

router = APIRouter(prefix="/auth", tags=["Authentication & Accounts"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    description="Registers a new user account with hashed password credentials in PostgreSQL."
)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    User registration endpoint.
    Checks if email already exists, hashes password with bcrypt, and stores new User record.
    """
    # Check if user email is already registered
    stmt = select(User).where(User.email == user_in.email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    # Hash plain-text password using salted bcrypt
    hashed_pwd = get_password_hash(user_in.password)

    # Instantiate new User model
    new_user = User(
        email=user_in.email,
        hashed_password=hashed_pwd,
        is_active=True
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post(
    "/login",
    response_model=Token,
    summary="User Login (OAuth2 Form / JSON)",
    description="Authenticates user credentials and returns a signed JWT Access Token."
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth2 compatible login endpoint.
    Accepts form-encoded `username` (email) and `password` parameters for standard Swagger UI compatibility.
    """
    # Query database for matching user by email (username field in OAuth2 form)
    stmt = select(User).where(User.email == form_data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account."
        )

    # Create signed JWT access token with user email subject claim
    access_token = create_access_token(data={"sub": user.email})

    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User Profile",
    description="Retrieves current authenticated user details using JWT Bearer token."
)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    """
    Protected user profile endpoint.
    Demonstrates retrieving current user via `Depends(get_current_user)`.
    """
    return current_user
