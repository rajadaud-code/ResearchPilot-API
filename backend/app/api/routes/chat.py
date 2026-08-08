"""
Chat & Streaming API Routes with Authenticated Persistent Memory & Rate Limiting.

===============================================================================
AUTHENTICATED SSE STREAMING & RATE LIMIT SECURITY
===============================================================================
1. Rate Limiting Security:
   - Endpoint protected by `@limiter.limit("10/minute")` using `slowapi`.
   - Prevents API credit exhaustion attacks by restricting clients to 10 streaming requests/min.

2. Security & Persistent Memory Workflow:
   - Protected by `current_user: User = Depends(get_current_user)`.
   - User Query is saved to database (`role="user"`) *before* streaming begins.
   - Stream tokens are emitted real-time over SSE while accumulating in-memory.
   - Upon completion, full synthesized response is committed to PostgreSQL (`role="assistant"`).
===============================================================================
"""

import json
import logging
from typing import List, AsyncGenerator
from fastapi import APIRouter, Depends, Query, Request, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.agents.research_agent import stream_research_agent_response
from app.api.dependencies import get_db, get_ai_model, get_current_user
from app.core.rate_limit import limiter
from app.models.user import User
from app.schemas.chat_schema import ChatMessageResponse
from app.services.ai_svc import ai_service

logger = logging.getLogger("research_pilot.chat")

router = APIRouter(prefix="/chat", tags=["Chat & AI Streaming"])


async def authenticated_event_generator(
    request: Request,
    query: str,
    user_id: int,
    db: AsyncSession
) -> AsyncGenerator[str, None]:
    """
    SSE Generator for authenticated users.
    Persists user query, streams tokens real-time, and commits assistant response upon completion.
    """
    logger.info(f"📡 Initiating authenticated SSE stream [User ID: {user_id}] for query: '{query}'")

    # 1. Save user query to database
    try:
        await ai_service.save_chat_message(db=db, user_id=user_id, role="user", content=query)
    except Exception as e:
        logger.error(f"❌ Failed to persist initial user query message: {str(e)}")

    accumulated_tokens: List[str] = []

    try:
        # Consume tokens from the autonomous agent generator
        async for token in stream_research_agent_response(query):
            if await request.is_disconnected():
                logger.warning(f"⚠️ Client [User {user_id}] disconnected mid-stream. Cancelling execution.")
                break

            accumulated_tokens.append(token)
            payload = json.dumps({"token": token, "type": "content"})
            yield f"data: {payload}\n\n"

        # 2. Persist complete assistant answer upon successful stream completion
        full_assistant_reply = "".join(accumulated_tokens).strip()
        if full_assistant_reply:
            try:
                await ai_service.save_chat_message(
                    db=db,
                    user_id=user_id,
                    role="assistant",
                    content=full_assistant_reply
                )
            except Exception as e:
                logger.error(f"❌ Failed to persist assistant response turn: {str(e)}")

        end_payload = json.dumps({"type": "end", "status": "completed"})
        yield f"event: end\ndata: {end_payload}\n\n"

    except Exception as e:
        logger.error(f"❌ Streaming error for user {user_id}: {str(e)}", exc_info=True)
        error_payload = json.dumps({"type": "error", "message": "Internal streaming error occurred."})
        yield f"event: error\ndata: {error_payload}\n\n"


@router.get(
    "/stream",
    response_class=StreamingResponse,
    summary="Stream Protected AI Research Response via SSE (Rate-Limited)",
    description=(
        "Establishes an authenticated Server-Sent Events (SSE) connection. "
        "Rate-limited to 10 requests per minute per IP address."
    )
)
@limiter.limit("10/minute")
async def stream_chat_response(
    request: Request,
    query: str = Query(..., min_length=1, description="Research question or query."),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    ai_model=Depends(get_ai_model),
):
    """
    Protected HTTP GET endpoint delivering real-time SSE stream.
    Rate limited to 10 requests/minute.
    """
    if not query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter cannot be empty."
        )

    return StreamingResponse(
        authenticated_event_generator(request, query, current_user.id, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Content-Type": "text/event-stream",
        }
    )


@router.get(
    "/history",
    response_model=List[ChatMessageResponse],
    summary="Get User Chat History",
    description="Retrieves the persistent conversation history turns stored in PostgreSQL for the authenticated user."
)
async def get_chat_history(
    limit: int = Query(50, ge=1, le=200, description="Max history messages to fetch."),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves chronological chat history turns for current user.
    """
    messages = await ai_service.get_user_chat_history(db=db, user_id=current_user.id, limit=limit)
    return messages
