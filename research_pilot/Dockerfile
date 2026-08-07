# ==============================================================================
# ResearchPilot API - Production Multi-Stage Dockerfile
# ==============================================================================
# Node.js Comparison: Similar to multi-stage Docker build for Node apps,
# installing dependencies in builder stage and copying compiled artifacts to runtime image.
# ==============================================================================

# --- Stage 1: Build Dependencies ---
FROM python:3.11-slim as builder

WORKDIR /app

# Prevent Python from writing .pyc files and buffer stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install OS build essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install wheels into a virtualenv directory
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Final Lightweight Production Runtime ---
FROM python:3.11-slim as runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Install PostgreSQL runtime client library
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application source code
COPY . .

# Create unprivileged application user for container security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# ==============================================================================
# GUNICORN PROCESS MANAGER WITH UVICORN WORKERS EXPLANATION
# ==============================================================================
# In production, running `uvicorn` directly limits execution to a single process.
# Gunicorn serves as a process manager:
#   - Master process monitors worker processes, handling restarts and OS signals (SIGTERM/SIGHUP).
#   - `-w 4` spawns 4 worker processes to utilize multi-core server CPUs.
#   - `-k uvicorn.workers.UvicornWorker` runs high-performance async Uvicorn worker instances.
# ==============================================================================
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
