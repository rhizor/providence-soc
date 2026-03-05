# Providence SOC - Dockerized Test Environment

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -s /bin/bash appuser

# Install Python dependencies
RUN pip install --no-cache-dir pytest pytest-cov pyyaml

# Copy all project files
COPY . .

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

ENV PYTHONPATH=/app

CMD ["pytest", "-v", "--tb=short"]
