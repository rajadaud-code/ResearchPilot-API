"""
Chat & Streaming API Routes.

===============================================================================
EXPRESS / NODE.JS VS. FASTAPI SSE (SERVER-SENT EVENTS) STREAMING
===============================================================================
In Node.js / Express:
  - SSE requires manually writing response headers:
      res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
      });
  - Chunks are manually written with `res.write(`data: ${JSON.stringify(chunk)}\n\n`)`.
  - Disconnect handling requires subscribing to `req.on('close', ...)` event listeners.

In FastAPI / Python (StreamingResponse + Async Generator):
  - `starlette.responses.StreamingResponse` accepts any Python `AsyncGenerator`.
  - FastAPI handles reading from the async generator and flushing data to the ASGI socket automatically.
  - SSE Protocol Requirements:
      1. Content-Type must be `text/event-stream`.
      2. Chunks MUST be prefixed with `data: ` and end with double newlines `\n\n`.
      3. `Cache-Control: no-cache` prevents proxy caching.
      4. `X-Accel-Buffering: no` prevents Nginx / reverse proxies from buffering tokens.
  - Client Disconnect Detection:
      Inside the async generator loop, calling `await request.is_disconnected()` returns `True` if the
      client closed the connection, allowing immediate cancellation of expensive LLM tasks.
===============================================================================
"""

import json
import logging
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, Query, Request, HTTPException, status
from fastapi.responses import StreamingResponse

from app.ai.agents.research_agent import stream_research_agent_response
from app.api.dependencies import get_ai_model

logger = logging.getLogger("research_pilot.chat")

router = APIRouter(prefix="/chat", tags=["Chat & AI Streaming"])


async def event_generator(request: Request, query: str) -> AsyncGenerator[str, None]:
    """
    Formatter generator wrapping the research agent async stream into W3C compliant SSE format.
    
    SSE Specification Format:
        data: <payload>\n\n
        
    If an event name or id is included:
        event: message\n
        id: 123\n
        data: <payload>\n\n
    """
    logger.info(f"📡 Initiating SSE stream for query: '{query}'")

    try:
        # Consume tokens from the autonomous agent async generator
        async for token in stream_research_agent_response(query):
            # Check if the client terminated the HTTP connection (e.g. browser tab closed)
            if await request.is_disconnected():
                logger.warning("⚠️ Client disconnected mid-stream. Halting AI execution pipeline.")
                break

            # Escape single newlines inside payload to preserve SSE line framing
            payload = json.dumps({"token": token, "type": "content"})
            
            # Yield properly formatted SSE line
            yield f"data: {payload}\n\n"

        # Signal completion with a custom SSE end event
        end_payload = json.dumps({"type": "end", "status": "completed"})
        yield f"event: end\ndata: {end_payload}\n\n"

    except Exception as e:
        logger.error(f"❌ Error during SSE streaming: {str(e)}", exc_info=True)
        error_payload = json.dumps({"type": "error", "message": "Internal streaming error occurred."})
        yield f"event: error\ndata: {error_payload}\n\n"


@router.get(
    "/stream",
    response_class=StreamingResponse,
    summary="Stream AI Research Agent Response via SSE",
    description=(
        "Establishes a Server-Sent Events (SSE) connection that streams autonomous document research tokens "
        "and agent reasoning steps in real-time."
    )
)
async def stream_chat_response(
    request: Request,
    query: str = Query(..., min_length=1, description="The research question or search query."),
    ai_model=Depends(get_ai_model),
):
    """
    HTTP GET endpoint delivering real-time SSE stream.
    
    Demonstrates:
      1. Query param validation via Pydantic (`Query(...)`).
      2. Dependency Injection (`Depends(get_ai_model)`).
      3. Returning `StreamingResponse` configured with `text/event-stream`.
    """
    if not query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter cannot be empty."
        )

    # Return StreamingResponse with SSE headers
    return StreamingResponse(
        event_generator(request, query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable Nginx response buffering for sub-100ms delivery
            "Content-Type": "text/event-stream",
        }
    )
