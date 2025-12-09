# Use Python 3.14 slim image
FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI backend
COPY . .

# Create output directory (Railway Volume will mount here)
RUN mkdir -p /app/output

# Expose backend port
EXPOSE 8000

# Railway sets PORT dynamically, but FastAPI must still listen on 8000
ENV PORT=8000

# Start Uvicorn (single worker is required for streaming)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
