# OpenClaw-Scan API Dockerfile
# Supports both demo mode (free) and x402 paid mode

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for YARA
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    libyara-dev \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY README.md ./
COPY clawdhub_scanner ./clawdhub_scanner
COPY scanner ./scanner
COPY tests ./tests

# Install Python dependencies with x402 support
RUN pip install --no-cache-dir -e ".[x402]"

# Create upload directory
RUN mkdir -p /tmp/clawdhub_scans

# Railway sets PORT env var automatically
ENV API_HOST=0.0.0.0
ENV API_PORT=8402

EXPOSE 8402

# Run API server
CMD ["python", "-m", "clawdhub_scanner.api"]
