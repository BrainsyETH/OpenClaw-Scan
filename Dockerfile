# OpenClaw-Scan x402 API Production Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy scanner package
COPY clawdhub_scanner ./clawdhub_scanner
COPY yara_rules ./yara_rules

# Copy API server
COPY api ./api

# Install dependencies
COPY api/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Create upload directory
RUN mkdir -p /tmp/clawdhub_scans

# Expose port
EXPOSE 8000

# Run API server
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
