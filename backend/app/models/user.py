"""
User Database ORM Model.

===============================================================================
SQLALCHEMY 2.0 ORM MODEL PATTERN
===============================================================================
In SQLAlchemy 2.0:
  - `Mapped[int]` defines the Python type hint for the attribute.
  - `mapped_column(...)` defines the database column constraints (Primary Key, Index, Unique, Default).
  - Relationships are declared explicitly using `relationship()`.
===============================================================================
"""

from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.chat import ChatMessage


class User(Base):
    """
    User model representing application accounts in PostgreSQL.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # One-to-Many Relationship with ChatMessage (User has many ChatMessages)
    chat_messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', is_active={self.is_active})>"
