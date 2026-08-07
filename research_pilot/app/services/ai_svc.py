"""
AI & Persistent Chat History Service Module.

===============================================================================
STATEFUL PERSISTENT MEMORY IN LLM PIPELINES
===============================================================================
In stateless LLM APIs (OpenAI / Claude), models do not retain memory across separate HTTP calls.
To maintain multi-turn conversational context:
  1. Incoming user queries must be stored in persistent storage (PostgreSQL).
  2. Generated AI response tokens must be accumulated and stored as "assistant" role turns upon stream completion.
  3. Prior chat turns are loaded from the database (`get_user_chat_history`) and formatted into
     LangChain `HumanMessage` and `AIMessage` memory lists before feeding to the LLM agent.
===============================================================================
"""

import logging
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage

logger = logging.getLogger("research_pilot.ai_svc")


class AIService:
    """
    Service layer handling AI domain logic, prompt formatting, and persistent chat history storage.
    """

    async def save_chat_message(
        self,
        db: AsyncSession,
        user_id: int,
        role: str,
        content: str
    ) -> ChatMessage:
        """
        Saves a single conversational interaction turn (user query or assistant response) to PostgreSQL.
        
        Args:
            db (AsyncSession): SQLAlchemy async database session.
            user_id (int): ID of user engaged in chat session.
            role (str): Sender role ("user" or "assistant").
            content (str): Text body of message.

        Returns:
            ChatMessage: Stored ChatMessage ORM model instance.
        """
        message = ChatMessage(
            user_id=user_id,
            role=role,
            content=content
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        
        logger.info(f"💾 Persisted chat message [ID: {message.id}, User: {user_id}, Role: '{role}']")
        return message

    async def get_user_chat_history(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = 50
    ) -> List[ChatMessage]:
        """
        Retrieves ordered chat interaction history for a specified user.
        
        Args:
            db (AsyncSession): SQLAlchemy async database session.
            user_id (int): Authenticated user ID.
            limit (int): Maximum history messages to retrieve.

        Returns:
            List[ChatMessage]: Chronologically ordered list of chat turns.
        """
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.timestamp.asc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        messages = result.scalars().all()
        return list(messages)


# Export singleton instance
ai_service = AIService()
