# Use Python 3.14 slim image
FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Install system dependencies (required for reportlab)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libfreetype6-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app
COPY . .

# Create output directory
RUN mkdir -p /app/output

# Expose backend port
EXPOSE 8000

ENV PORT=8000

# Start FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
