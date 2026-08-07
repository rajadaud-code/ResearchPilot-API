"""
SQLAlchemy 2.0 Base Model.

===============================================================================
EXPRESS / NODE.JS ORM VS. SQLALCHEMY 2.0 DECLARATIVE BASE
===============================================================================
In Node.js (Prisma / TypeORM / Sequelize):
  - Models are defined in `.prisma` files or annotated TypeScript classes (`@Entity()`).
  - Table mappings rely on decorators or code generation CLI binaries (`prisma generate`).

In Python / SQLAlchemy 2.0:
  - Models inherit from a central `DeclarativeBase`.
  - Type-safe column definitions use modern `Mapped[T]` and `mapped_column()` functions.
  - Python typing integrates directly with IDE autocomplete and static type checkers (Mypy/Pyright).
===============================================================================
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM database models.
    Provides standard metadata registration for database migrations (e.g. Alembic).
    """
    pass
