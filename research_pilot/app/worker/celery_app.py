"""
Celery Task Queue Application Initialization.

===============================================================================
EXPRESS / NODE.JS BULLMQ VS. PYTHON CELERY
===============================================================================
In Node.js:
  - Heavy background processing (e.g. video processing, PDF parsing) uses BullMQ or Bee-Queue backed by Redis.
  - Workers run as separate Node processes consuming jobs from Redis queues.

In Python:
  - Celery is the standard distributed task queue framework in Python.
  - Celery offloads CPU-heavy tasks (e.g. document embedding generation, OCR, fine-tuning) out of the
    main async event loop into dedicated worker processes.
  - Uses Redis or RabbitMQ as the message broker (`CELERY_BROKER_URL`).
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
)
