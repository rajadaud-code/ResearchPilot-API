"""
WebSocket Connection Manager.

===============================================================================
EXPRESS / NODE.JS VS. FASTAPI WEBSOCKET MONITORING
===============================================================================
In Node.js:
  - WebSockets use `ws` or `socket.io` instances to manage socket rooms and task progress channels.

In FastAPI:
  - Native `WebSocket` objects handle full-duplex ASGI communication over standard HTTP upgrades.
  - The `ConnectionManager` maintains active socket dictionaries keyed by `task_id`, allowing real-time
    push updates of Celery document ingestion progress directly to frontend clients without polling overhead.
===============================================================================
"""

import json
import logging
from typing import Dict, List
from fastapi import WebSocket

logger = logging.getLogger("research_pilot.websockets")


class ConnectionManager:
    """
    Manages active WebSocket connections grouped by task_id and global broadcast subscriptions.
    """
    def __init__(self):
        # Map of task_id -> List[WebSocket]
        self.task_connections: Dict[str, List[WebSocket]] = {}
        # List of all active global WebSockets
        self.active_connections: List[WebSocket] = []

    async def connect_task(self, websocket: WebSocket, task_id: str):
        """Accepts a WebSocket connection and registers it under a specific task_id."""
        await websocket.accept()
        if task_id not in self.task_connections:
            self.task_connections[task_id] = []
        self.task_connections[task_id].append(websocket)
        self.active_connections.append(websocket)
        logger.info(f"🔌 WebSocket client connected for Task ID: {task_id}")

    def disconnect_task(self, websocket: WebSocket, task_id: str):
        """Removes a disconnected WebSocket connection from tracking registries."""
        if task_id in self.task_connections and websocket in self.task_connections[task_id]:
            self.task_connections[task_id].remove(websocket)
            if not self.task_connections[task_id]:
                del self.task_connections[task_id]
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"🔌 WebSocket client disconnected for Task ID: {task_id}")

    async def send_task_update(self, task_id: str, data: dict):
        """Sends a JSON status payload to all clients listening to a specific task_id."""
        if task_id in self.task_connections:
            message = json.dumps(data)
            disconnected = []
            for connection in self.task_connections[task_id]:
                try:
                    await connection.send_text(message)
                except Exception:
                    disconnected.append(connection)
            
            for conn in disconnected:
                self.disconnect_task(conn, task_id)

    async def broadcast(self, message: str):
        """Broadcasts a plain text message to all active WebSocket clients."""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass


# Global connection manager instance
manager = ConnectionManager()
