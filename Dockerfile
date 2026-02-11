# OpenClaw-Scan x402 API Production Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md ./
COPY clawdhub_scanner ./clawdhub_scanner
COPY api ./api

# Install core dependencies first (guaranteed to work)
RUN pip install --no-cache-dir -e ".[api]"

# Install x402 extras separately — if it fails, API still works in demo mode
RUN pip install --no-cache-dir "x402[fastapi,evm]>=2.0.0" || \
    echo "[x402] x402 SDK not available — API will run in demo mode"

# Create upload directory
RUN mkdir -p /tmp/clawdhub_scans

# Railway sets PORT env var at runtime
ENV API_HOST=0.0.0.0

EXPOSE 8402

CMD python -m clawdhub_scanner.api
