"""
WebSocket Connection Manager.

===============================================================================
EXPRESS / NODE.JS WS VS. FASTAPI WEBSOCKET MANAGER
===============================================================================
In Node.js:
  - WebSocket servers are commonly managed via `ws` or `Socket.io` instances attached to the HTTP server.

In FastAPI:
  - FastAPI provides native `WebSocket` objects representing bidirectional ASGI connections.
  - A `ConnectionManager` class maintains a list of active sockets, handling broadcast messaging
    and disconnect cleanup gracefully.
===============================================================================
"""

from typing import List
from fastapi import WebSocket


class ConnectionManager:
    """
    Manages active WebSocket client connections for real-time bi-directional streaming.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()
