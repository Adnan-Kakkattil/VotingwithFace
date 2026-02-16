# College Voting System - Docker
FROM python:3.11-slim

WORKDIR /app

# Install system deps for dlib/opencv (if building from source)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libopenblas-dev \
    libx11-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create upload directories
RUN mkdir -p uploads face_encodings

# Expose port
EXPOSE 5000

# Run seed and start server
CMD python -m scripts.seed_admin 2>/dev/null || true && \
    python run.py
