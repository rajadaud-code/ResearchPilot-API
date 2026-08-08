"""
Application Configuration Module.

===============================================================================
EXPRESS / NODE.JS VS. FASTAPI / PYDANTIC SETTINGS ARCHITECTURE
===============================================================================
In Node.js / Express:
  - Configuration is often loaded globally via `require('dotenv').config()`.
  - Environment variables are accessed directly from `process.env.VARIABLE_NAME`.
  - Type conversion and validation must be written manually (or using libs like `dotenv-safe` or `zod`).
  - Missing or mistyped env variables often trigger silent bugs or unexpected `undefined` runtime failures.

In FastAPI / Python (Pydantic v2 BaseSettings):
  - `pydantic-settings` reads `.env` files and environment variables, coercing types automatically
    (e.g., string "true" -> bool True, string "8000" -> int 8000).
  - Schema validation occurs at startup: if a required variable is missing or has an invalid type,
    the app fails fast before serving traffic, preventing runtime configuration errors.
  - The configuration object is immutable, strongly typed, and autocompleted across your IDE.
===============================================================================
"""

from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings class backed by Pydantic v2.
    Attributes defined here map directly to `.env` variables or system environment variables.
    """

    # --- Core Application Config ---
    PROJECT_NAME: str = "ResearchPilot API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # --- PostgreSQL Database Settings ---
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "research_pilot_db"
    
    # Fully qualified SQLAlchemy Database Connection URI (Async Driver: asyncpg)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/research_pilot_db"

    # --- Vector Database Settings ---
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000

    # --- Redis & Celery Task Queue Settings ---
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # --- AI Model Provider Keys ---
    OPENAI_API_KEY: str = "sk-placeholder-key-for-development"

    # --- Security & CORS ---
    SECRET_KEY: str = "super-secret-development-key-change-in-production"
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """
        Validator to handle CORS origins defined as JSON strings or comma-separated values in .env.
        In Node.js, parsing array env vars requires manual `process.env.ORIGINS.split(',')`.
        Pydantic field validators automate this safely.
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(f"Invalid CORS origins format: {v}")

    # Pydantic v2 Settings configuration: loads from `.env` with case-insensitive matching
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Instantiate a global singleton settings object.
# In Python/FastAPI, importing `settings` provides type-safe, validated application settings anywhere.
settings = Settings()
