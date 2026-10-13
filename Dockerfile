# Multi-stage Dockerfile for Litera Backend & MCP Server
# Course: Human-Computer Interaction Design (HCI) / BSU FAMCS 2026
# Authors: Kirill Zaidal, Anna-Maria Savitskaya (Group 12)

# ==============================================================================
# Stage 1: Build & Dependencies
# ==============================================================================
FROM python:3.11-slim AS builder

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY mcp-server/requirements.txt ./mcp-requirements.txt
RUN pip install --prefix=/install -r mcp-requirements.txt || true

# ==============================================================================
# Stage 2: Final Runtime Environment
# ==============================================================================
FROM python:3.11-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PYTHONPATH=/app:/app/mcp-server

RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -s /bin/bash -m appuser

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source code
COPY --chown=appuser:appgroup database /app/database
COPY --chown=appuser:appgroup api /app/api
COPY --chown=appuser:appgroup mcp-server /app/mcp-server

USER appuser

EXPOSE 8000 5005

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python3 -c "from storage import LiteraStorage; s = LiteraStorage(':memory:'); exit(0 if len(s.get_catalog()) > 0 else 1)"

CMD ["python3", "mcp-server/server.py"]
