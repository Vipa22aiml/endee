FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[all]"

# Copy source code
COPY src/ src/

# Create cache directory for local models
RUN mkdir -p /app/cache

ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/app/cache

# Default command (stdio transport)
CMD ["python", "-m", "endee_mcp"]
