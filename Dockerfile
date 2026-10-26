# Use official lightweight Python 3.13 base image
FROM python:3.13-slim

# Install system dependencies (curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv by copying pre-compiled binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy dependency definition files first for optimal layer caching
COPY pyproject.toml README.md ./

# Install project dependencies into virtual environment
RUN uv sync --frozen --no-dev --no-install-project 2>/dev/null || uv sync --no-dev --no-install-project

# Copy application source code
COPY src ./src
COPY tests ./tests

# Install the application package itself
RUN uv sync --no-dev

# Place virtual environment on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose web application port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start FastAPI application
CMD ["uv", "run", "python-postgresql-crud"]
