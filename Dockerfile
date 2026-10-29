# Production Deployment Container for Vesper Service
FROM ubuntu:22.04

# Prevent interactive prompts during apt installation
ENV DEBIAN_FRONTEND=noninteractive

# Install compilers, runtimes, and system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    g++ \
    gcc \
    python3 \
    python3-pip \
    openjdk-17-jdk \
    time \
    coreutils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy dependency specifications first (layer caching)
COPY requirements.txt pyproject.toml ./

# Install Python requirements
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy complete project codebase
COPY . .

# Expose Vesper REST API & Studio UI port
ENV PORT=8000
EXPOSE 8000

# Set healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/api/health || exit 1

# Start Uvicorn ASGI production server with dynamic port support
CMD ["sh", "-c", "python3 -m uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}"]
