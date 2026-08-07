"""
Document Management Router.

Demonstrates vector store integration and async DB operations.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.dependencies import get_vector_db

router = APIRouter(prefix="/documents", tags=["Document Management"])


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    chunks_indexed: int


@router.get(
    "/search",
    summary="Vector Search Documents",
    description="Perform semantic vector similarity search against indexed document embeddings in ChromaDB."
)
async def search_documents(
    query: str,
    limit: int = 5,
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
