"""
Chat Schemas for Request Validation and Response Serialization.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message in persistent history."""
    role: str = Field(..., description="Role of message sender ('user' or 'assistant').")
    content: str = Field(..., description="Text content of message.")


class ChatMessageResponse(BaseModel):
    """Schema for returning chat history items."""
    id: int
    user_id: int
    role: str
    content: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatStreamQuery(BaseModel):
    """Schema for streaming research agent queries."""
    query: str = Field(..., min_length=1, description="Research query or search question.")
