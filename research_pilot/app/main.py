"""
ResearchPilot API Main Application Entry Point.

===============================================================================
EXPRESS / NODE.JS VS. FASTAPI PRODUCTION ARCHITECTURE
===============================================================================
In Node.js:
  - PM2 or Cluster module spawns multiple Node process instances.

In FastAPI / Python (Gunicorn + Uvicorn Worker Process Manager):
  - Gunicorn acts as a master process manager managing master worker signals.
  - `uvicorn.workers.UvicornWorker` runs high-performance async worker processes.
  - Multi-core CPU utilization is achieved across Gunicorn worker processes (`-w 4`).
  - SlowAPI middleware intercepts incoming requests to enforce IP-based rate limiting.
  - WebSockets & SSE endpoints stream non-blocking I/O over standard ASGI protocol.
===============================================================================
"""

import logging
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.lifespan import lifespan
from app.core.rate_limit import limiter
from app.api.routes import auth, documents, chat, websockets

# Configure logger
logger = logging.getLogger("research_pilot.main")

# Instantiate FastAPI App with Lifespan Context Manager
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",      # Interactive Swagger UI docs
    redoc_url="/redoc",    # ReDoc documentation UI
    lifespan=lifespan,     # Standard ASGI lifespan for state management
)

# -----------------------------------------------------------------------------
# Rate Limiter Configuration (SlowAPI)
# -----------------------------------------------------------------------------
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# -----------------------------------------------------------------------------
# CORS Middleware Configuration
# -----------------------------------------------------------------------------
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# -----------------------------------------------------------------------------
# Router Registrations
# -----------------------------------------------------------------------------
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(documents.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)
app.include_router(websockets.router, prefix=settings.API_V1_STR)


# -----------------------------------------------------------------------------
# Root & Health Check Endpoints
# -----------------------------------------------------------------------------
@app.get("/", tags=["Health"])
async def root_welcome():
    """
    Root welcome endpoint displaying API identity and documentation links.
    """
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "documentation": "/docs",
        "status": "online"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Service health check endpoint for monitoring tools (Kubernetes / AWS ECS liveness probes).
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
            "database": "connected (mock)",
            "vector_store": "connected (mock)",
            "ai_model": "loaded (mock)"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
