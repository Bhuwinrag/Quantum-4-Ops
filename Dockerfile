# QUANTUM//OPS - Quantum Hybrid Computing Workbench Dockerfile
# Standard Multi-Arch Linux CPU / GPU Simulation Image

# Base Python runtime (Python 3.11)
FROM python:3.11-slim

# Labels & Metadata
LABEL maintainer="QUANTUM//OPS Team <bhuwin@quantumops.dev>"
LABEL description="QUANTUM//OPS - Quantum Hybrid Computing Workbench"
LABEL version="1.0.0-PROD"

# Set environment flags
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    QUANTUM_ENV=production \
    HOST=0.0.0.0 \
    PORT=8000 \
    DEFAULT_SIMULATION_BACKEND=cpu_simulator

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency specifications first for Docker layer caching
COPY requirements.txt .

# Install Python requirements
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# (Optional: On Linux x86_64, CUDA-Q can be installed directly)
# RUN pip install --no-cache-dir cudaq || true

# Copy project codebase
COPY . .

# Expose FastAPI workbench port
EXPOSE 8000

# Health check probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Production startup command
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
