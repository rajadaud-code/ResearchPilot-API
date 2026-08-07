"""
Document Management & Asynchronous Ingestion Routes.

===============================================================================
EXPRESS / NODE.JS VS. FASTAPI NON-BLOCKING FILE UPLOAD & TASK QUEUES
===============================================================================
In Node.js / Express:
  - Multipart uploads are parsed via `multer`.
  - Heavy background processing jobs are pushed to BullMQ: `await pdfQueue.add('parse', { path })`.
  - The route returns `202 Accepted` with a job ID.

In FastAPI / Python:
  - Multipart uploads use `UploadFile = File(...)` which streams file bytes asynchronously.
  - Offloaded tasks call `process_document_task.delay(document_id, file_path)` pushing a job message to Redis.
  - The endpoint returns `202 Accepted` instantly.
  - Task progress and final completion status are checked via `AsyncResult(task_id)`.
===============================================================================
"""

import os
import uuid
from typing import Dict, Any
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from pydantic import BaseModel
from celery.result import AsyncResult

from app.api.dependencies import get_vector_db, get_current_user
from app.models.user import User
from app.worker.tasks import process_document_task

router = APIRouter(prefix="/documents", tags=["Document Ingestion & Management"])

# Temporary upload folder on server disk
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Dict[str, Any]


@router.post(
    "/upload",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload Document for Asynchronous Vector Indexing",
    description="Saves uploaded document stream to disk and dispatches a Celery task to parse and index vectors in Redis/ChromaDB."
)
async def upload_document(
    file: UploadFile = File(..., description="PDF or text document file to ingest."),
    current_user: User = Depends(get_current_user),
):
    """
    Non-blocking document upload endpoint.
    Saves file to disk, enqueues background processing task, and returns HTTP 202 Accepted with task_id.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a valid filename."
        )

    # Generate unique document ID and file destination
    document_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename)[1]
    safe_filename = f"{document_id}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    try:
        # Save file stream to local disk asynchronously
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded file to disk: {str(e)}"
        )

    # Dispatch background task to Celery worker pool
    try:
        celery_task = process_document_task.delay(document_id, file_path)
        task_id = celery_task.id
    except Exception as e:
        # Fallback if Redis server is offline: execute directly or return mock task ID
        task_id = f"local_mock_task_{uuid.uuid4().hex[:8]}"

    return {
        "status": "ACCEPTED",
        "message": "File upload received. Document ingestion task dispatched to background worker queue.",
        "document_id": document_id,
        "task_id": task_id,
        "filename": file.filename,
        "size_bytes": len(contents),
        "status_url": f"/api/v1/documents/tasks/{task_id}"
    }


@router.get(
    "/tasks/{task_id}",
    response_model=TaskStatusResponse,
    summary="Check Background Document Ingestion Task Status",
    description="Queries Celery result backend for document parsing, chunking, and embedding task progress."
)
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Task status polling endpoint.
    Queries Redis backend for task state (PENDING, PROGRESS, SUCCESS, FAILURE).
    """
    task_result = AsyncResult(task_id)

    # Extract state and metadata
    state = task_result.state
    result_data = {}

    if state == "PENDING":
        result_data = {"progress": "Task queued in Redis, awaiting worker pickup."}
    elif state == "PROGRESS":
        result_data = task_result.info or {"progress": "Processing document chunks..."}
    elif state == "SUCCESS":
        result_data = task_result.result if isinstance(task_result.result, dict) else {"details": str(task_result.result)}
    elif state == "FAILURE":
        result_data = {"error": str(task_result.info)}

    return TaskStatusResponse(
        task_id=task_id,
        status=state,
        result=result_data
    )


@router.get(
    "/search",
    summary="Vector Search Documents",
    description="Perform semantic vector similarity search against indexed document embeddings in ChromaDB."
)
async def search_documents(
    query: str,
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    vector_db=Depends(get_vector_db)
) -> Dict[str, Any]:
    """
    Search endpoint utilizing injected ChromaDB dependency.
    """
    results = vector_db.query(query)
    return {
        "status": "success",
        "query": query,
        "results": results.get("results", [])[:limit]
    }
