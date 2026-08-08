"""
Celery Task Queue Application Initialization.

===============================================================================
EXPRESS / NODE.JS BULLMQ VS. PYTHON CELERY
===============================================================================
In Node.js:
  - Background workers use BullMQ with Redis streams/queues to offload long-running tasks out of the HTTP thread.

In Python:
  - Celery is the industry standard distributed task queue for Python backend systems.
  - Heavy tasks (such as PDF text extraction, OCR, vector embedding calculation) run in separate Celery
    worker processes, leaving the FastAPI `asyncio` event loop responsive to incoming HTTP/SSE connections.
  - State and results are persisted in the Redis backend (`CELERY_RESULT_BACKEND`).
===============================================================================
"""

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "research_pilot_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    result_expires=3600,  # Expire task results after 1 hour
)
