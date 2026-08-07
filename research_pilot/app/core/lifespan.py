"""
FastAPI Lifespan Context Manager Module.

===============================================================================
EXPRESS / NODE.JS VS. FASTAPI LIFESPAN ARCHITECTURE
===============================================================================
In Node.js / Express:
  - Application setup typically occurs top-to-bottom in index.js before `app.listen()`.
  - Database client connection pools, Redis clients, and background listeners are initialized globally
    or attached manually to express app state (`app.set('db', db)`).
  - Graceful shutdown requires manual process signal handling (`process.on('SIGTERM', ...)`), closing server
    listeners, draining DB pools, and terminating open sockets manually.

In FastAPI (ASGI Lifespan standard using @asynccontextmanager):
  - Lifespan context managers replace older event hooks (`@app.on_event("startup")` / `"shutdown"`).
  - Code BEFORE the `yield` runs when the server boots up (allocating state like DB pools, vector stores, AI weights).
  - Global state is stored cleanly on `app.state` (accessible to requests via FastAPI `Request.app.state`).
  - Code AFTER the `yield` executes automatically when the server shuts down (freeing GPU memory, closing DB connections).
  - Ensures atomic, fail-safe lifecycle handling natively supported by ASGI servers like Uvicorn.
===============================================================================
"""

from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator, Any, Dict
from fastapi import FastAPI

# Setup logger for startup and shutdown feedback
logger = logging.getLogger("research_pilot.lifespan")
logging.basicConfig(level=logging.INFO)


class MockChromaDBClient:
    """
    Mock Vector Store client simulating a connection to ChromaDB.
    Demonstrates how expensive connections are initialized once during lifespan startup.
    """
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.is_connected = False

    async def connect(self) -> None:
        self.is_connected = True
        logger.info(f"🟢 [ChromaDB] Connected to vector store cluster at {self.host}:{self.port}")

    async def close(self) -> None:
        self.is_connected = False
        logger.info("🔴 [ChromaDB] Vector store connection pool gracefully closed.")

    def query(self, text: str) -> Dict[str, Any]:
        return {
            "query": text,
            "results": [
                {"id": "doc_101", "score": 0.94, "content": "Vector embedding matching query context."},
                {"id": "doc_102", "score": 0.88, "content": "Secondary relevance research paper segment."}
            ]
        }


class MockAIModel:
    """
    Mock AI Model wrapper simulating heavy LLM / Embedding model weights loaded into memory on startup.
    """
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.is_loaded = False

    async def load_weights(self) -> None:
        self.is_loaded = True
        logger.info(f"🧠 [AI Model] Loaded model weights for '{self.model_name}' into memory.")

    async def unload_weights(self) -> None:
        self.is_loaded = False
        logger.info(f"🧠 [AI Model] Unloaded model weights for '{self.model_name}'. Memory freed.")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPI Lifespan context manager.
    Handles startup resources (Vector DB, LLM models, Database pools) and ensures clean teardown.
    """
    # -------------------------------------------------------------------------
    # 1. STARTUP PHASE (Executed before the application starts accepting requests)
    # -------------------------------------------------------------------------
    logger.info("🚀 [Startup] Initializing ResearchPilot API services & global state...")

    # Initialize ChromaDB Vector Database Client connection
    chroma_client = MockChromaDBClient(host="localhost", port=8000)
    await chroma_client.connect()

    # Initialize AI Model pipeline
    ai_model = MockAIModel(model_name="gpt-4o-mini-researcher")
    await ai_model.load_weights()

    # Attach initialized global state objects to `app.state`.
    # FastAPI exposes `app.state` to all route handlers via Dependency Injection (`Request.app.state`).
    app.state.vector_db = chroma_client
    app.state.ai_model = ai_model

    logger.info("✅ [Startup] Global application state initialized successfully.")

    # -------------------------------------------------------------------------
    # 2. YIELD CONTROL (Application is active and serving HTTP/SSE/WebSocket traffic)
    # -------------------------------------------------------------------------
    yield

    # -------------------------------------------------------------------------
    # 3. SHUTDOWN PHASE (Executed when Uvicorn receives SIGTERM/SIGINT)
    # -------------------------------------------------------------------------
    logger.info("🛑 [Shutdown] Draining connections and freeing application resources...")

    # Gracefully shut down clients and release memory
    await app.state.vector_db.close()
    await app.state.ai_model.unload_weights()

    logger.info("👋 [Shutdown] ResearchPilot API shutdown complete.")
