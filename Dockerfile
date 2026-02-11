# OpenClaw-Scan API Dockerfile
# Supports both demo mode (free) and x402 paid mode

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for YARA
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY clawdhub_scanner ./clawdhub_scanner
COPY tests ./tests
COPY README.md ./

# Install Python dependencies
# Use 'api' extra for demo mode, 'x402' extra for paid mode
ARG INSTALL_MODE=api
RUN pip install --no-cache-dir -e ".[$INSTALL_MODE]"

# Create upload directory
RUN mkdir -p /tmp/clawdhub_scans

# Expose default API port
EXPOSE 8402

# Run API server
CMD ["python", "-m", "clawdhub_scanner.api"]
