FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server
COPY pmwiki_mcp_server.py .

# Expose SSE port
EXPOSE 3000

CMD ["python", "-u", "pmwiki_mcp_server.py"]