"""
WebSocket Real-Time Progress Monitoring Routes.

===============================================================================
REAL-TIME TASK MONITORING OVER WEBSOCKETS
===============================================================================
Allows frontend clients to establish a persistent bi-directional socket connection
to receive real-time document chunking and vector embedding progress updates.
===============================================================================
"""

import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from celery.result import AsyncResult

from app.api.websockets.manager import manager

logger = logging.getLogger("research_pilot.ws_routes")

router = APIRouter(prefix="/ws", tags=["Real-Time WebSockets"])


@router.websocket("/task-updates/{task_id}")
async def websocket_task_updates(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint streaming live status updates for a specific Celery task_id.
    
    Usage:
        ws = new WebSocket("ws://localhost:8000/api/v1/ws/task-updates/{task_id}");
        ws.onmessage = (event) => console.log(JSON.parse(event.data));
    """
    await manager.connect_task(websocket, task_id)

    try:
        # Send connection confirmation payload
        await websocket.send_json({
            "type": "connection_established",
            "task_id": task_id,
            "message": f"Connected to real-time status stream for task: {task_id}"
        })

        # Monitor Celery AsyncResult status in a non-blocking loop
        previous_state = None
        while True:
            task_result = AsyncResult(task_id)
            current_state = task_result.state
            result_meta = task_result.info if isinstance(task_result.info, dict) else {"details": str(task_result.info)}

            # Send update if state changed or task is in progress
            update_payload = {
                "type": "task_progress_update",
                "task_id": task_id,
                "status": current_state,
                "meta": result_meta
            }
            
            await manager.send_task_update(task_id, update_payload)

            # Exit monitoring loop if task completed or failed
            if current_state in ["SUCCESS", "FAILURE", "REVOKED"]:
                logger.info(f"🏁 Task {task_id} reached terminal state '{current_state}'. Closing WS stream.")
                break

            # Poll interval (0.5 seconds)
            await asyncio.sleep(0.5)

    except WebSocketDisconnect:
        manager.disconnect_task(websocket, task_id)
        logger.info(f"🔌 Client disconnected from WebSocket task stream: {task_id}")
    except Exception as e:
        logger.error(f"❌ Error in WebSocket stream for task {task_id}: {str(e)}")
        manager.disconnect_task(websocket, task_id)
