"""
FastAPI Dependency Injection Module.

===============================================================================
EXPRESS / NODE.JS VS. FASTAPI AUTHENTICATION DEPENDENCIES
===============================================================================
In Node.js / Express:
  - Auth middleware parses `req.headers.authorization`, verifies token, and attaches `req.user = user`.
  - Protected routes must explicitly include middleware in route definitions:
      router.get('/protected', authMiddleware, handler);

In FastAPI (`OAuth2PasswordBearer` + `Depends(get_current_user)`):
  - `OAuth2PasswordBearer` extracts Bearer tokens automatically from the Authorization header
    and populates interactive Swagger UI `/docs` with an "Authorize" lock button.
  - Route handlers simply add `current_user: User = Depends(get_current_user)` to parameter signatures.
  - FastAPI handles dependency resolution, token extraction, database user lookup, error handling,
    and automatic injection of the `User` ORM instance.
===============================================================================
"""

from typing import AsyncGenerator
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings
from app.core.security import decode_access_token
from app.models.user import User

# Create SQLAlchemy 2.0 Async Engine using asyncpg driver
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,  # Automatically verify connections before checkout
)

# Async session factory for creating request-scoped database sessions
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# OAuth2 Password Bearer scheme pointing to the login token URL
# In Swagger UI (/docs), this unlocks the "Authorize" button for testing JWT protected routes
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency generator for acquiring an asynchronous database session.
    Yields an `AsyncSession` for the duration of the HTTP request and handles cleanup automatically.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_vector_db(request: Request):
    """
    Dependency function to retrieve the global ChromaDB client from `app.state`.
    """
    vector_db = getattr(request.app.state, "vector_db", None)
    if vector_db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector database service is not initialized."
        )
    return vector_db


async def get_ai_model(request: Request):
    """
    Dependency function to retrieve the global pre-loaded AI model from `app.state`.
    """
    ai_model = getattr(request.app.state, "ai_model", None)
    if ai_model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI research model service is not initialized."
        )
    return ai_model


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency to validate JWT access token and retrieve the current authenticated user from database.
    
    Args:
        token (str): JWT Bearer token extracted automatically by `OAuth2PasswordBearer`.
        db (AsyncSession): Request-scoped database session.

    Returns:
        User: Authenticated SQLAlchemy User model instance.

    Raises:
        HTTPException: HTTP 401 Unauthorized if token is invalid or user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode and verify JWT token payload signature
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # Extract user subject claim (email)
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    # Query database asynchronously for active user
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account."
        )

    return user
