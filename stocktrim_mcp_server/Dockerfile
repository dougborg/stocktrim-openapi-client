# StockTrim MCP Server - Dockerfile
# Builds a containerized version of the MCP server for Docker Desktop integration

FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install the package and its dependencies
# stocktrim-openapi-client will be installed from PyPI
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Set environment variables for logging
ENV LOG_FORMAT=json \
    LOG_LEVEL=INFO

# Expose MCP server on stdio (standard for MCP servers)
# The server runs via the entry point defined in pyproject.toml
CMD ["stocktrim-mcp-server"]
