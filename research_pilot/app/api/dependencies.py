"""
FastAPI Dependency Injection Module.

===============================================================================
EXPRESS / NODE.JS VS. FASTAPI DEPENDENCY INJECTION (Depends())
===============================================================================
In Node.js / Express:
  - Request contextual objects (DB clients, auth tokens, current user) are manually attached to `req`:
      app.use((req, res, next) => { req.db = dbPool; next(); });
  - Sub-functions rely on parameters passed down manually from controller functions.
  - Resource cleanup (closing DB sessions or transaction rollbacks) must be done imperatively inside
    `try/catch/finally` blocks inside every route handler or custom wrapper.

In FastAPI (`Depends()` architecture):
  - Dependencies are declared declaratively in route parameter lists:
      async def my_route(db: AsyncSession = Depends(get_db)):
  - FastAPI executes dependencies *before* the route runs, resolving entire dependency trees automatically.
  - Generator dependencies using `yield` allow setup logic BEFORE `yield` and teardown logic AFTER `yield`.
    FastAPI guarantees teardown code runs AFTER the response is returned to the client (or if an exception occurs).
  - Promotes modular, easily testable design—dependencies can be overridden in unit tests (`app.dependency_overrides`).
===============================================================================
"""

from typing import AsyncGenerator
from fastapi import Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings

# Create SQLAlchemy 2.0 Async Engine using asyncpg driver
# In Express, this is comparable to initializing a pg `Pool` singleton.
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


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency generator for acquiring an asynchronous database session.
    Yields an `AsyncSession` for the duration of the HTTP request and handles cleanup automatically.
    
    Yields:
        AsyncSession: Active SQLAlchemy async session.
    """
    async with AsyncSessionLocal() as session:
        try:
            # Yield session to the route handler / dependency subscriber
            yield session
            # Auto-commit on clean completion if needed by business logic
            await session.commit()
        except Exception:
            # Rollback transaction on exception
            await session.rollback()
            raise
        finally:
            # Session is closed automatically when exiting `async with` context
            await session.close()


async def get_vector_db(request: Request):
    """
    Dependency function to retrieve the global ChromaDB client from `app.state`.
    Demonstrates how request handlers safely access lifespan-initialized application state.
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
