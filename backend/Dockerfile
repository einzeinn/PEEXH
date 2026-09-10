# syntax=docker/dockerfile:1
# PEEXH Backend — Production Dockerfile

# --------------------------------------------------------------------------- #
# Builder stage: install Python dependencies in a lightweight venv             #
# --------------------------------------------------------------------------- #
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build essentials for any compiled packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --------------------------------------------------------------------------- #
# Runtime stage: minimal image with only what is needed at runtime             #
# --------------------------------------------------------------------------- #
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY . .

# Non-root user for security
RUN useradd -m -u 1000 peexh && chown -R peexh /app
USER peexh

# PEEXH backend binds to this port by default
EXPOSE 8000

# Health check so orchestrators can detect startup completion
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Launch with Uvicorn using 1 worker (websocket-compatible)
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
