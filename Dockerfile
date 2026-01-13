# HTTPAceProxy with NewEra Plugin
FROM python:3.11-slim

# Metadata
LABEL maintainer="HTTPAceProxy"
LABEL description="HTTPAceProxy server with NewEra plugin for Ace Stream"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY acehttp.py .
COPY aceconfig.py .
COPY acedefconfig.py .
COPY aceclient/ ./aceclient/
COPY modules/ ./modules/
COPY plugins/ ./plugins/
COPY http/ ./http/

# Copy entrypoint script
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# Create volume mount points
VOLUME ["/app/logs"]

# Expose HTTP port
EXPOSE 8888

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8888/stat || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV ACEPROXY_HOST=0.0.0.0
ENV ACEPROXY_PORT=8888

# Set entrypoint
ENTRYPOINT ["./docker-entrypoint.sh"]

# Default command (can be overridden)
CMD []
