"""
ResearchPilot API Main Application Entry Point.

===============================================================================
EXPRESS / NODE.JS VS. FASTAPI APPLICATION SETUP
===============================================================================
In Node.js / Express:
  - `const app = express();` initializes an Express app instance.
  - Middlewares are mounted via `app.use(cors())`, `app.use(express.json())`.
  - Routers are mounted via `app.use('/api/v1/chat', chatRouter)`.
  - The server starts via `app.listen(port, () => ...)` running on single-threaded event loop.

In FastAPI / Python (ASGI Web Standard):
  - `app = FastAPI(lifespan=lifespan)` initializes the web application.
  - ASGI (Asynchronous Server Gateway Interface) standard allows asynchronous Python servers (like Uvicorn)
    to handle thousands of concurrent HTTP, SSE, and WebSocket connections efficiently.
  - OpenAPI (Swagger UI) documentation is generated automatically from Pydantic schemas and type hints at `/docs`.
  - Middlewares (like `CORSMiddleware`) wrap the ASGI application stack cleanly.
  - `app.include_router(chat.router, prefix=settings.API_V1_STR)` mounts modular routers.
===============================================================================
"""

import logging
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.lifespan import lifespan
from app.api.routes import auth, documents, chat

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
# CORS Middleware Configuration
# -----------------------------------------------------------------------------
# In Express: `app.use(cors({ origin: ['http://localhost:3000'], credentials: true }))`
# In FastAPI: `CORSMiddleware` intercepts requests to handle preflight OPTIONS requests.
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
# In Express: `app.use('/api/v1/auth', authRouter)`
# In FastAPI: `app.include_router(auth.router, prefix="/api/v1")`
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(documents.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)


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


# Standard execution block when executing `python app/main.py` directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
