FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Cloud Run requires dynamic PORT
ENV PORT=8080

# 🔥 CRITICAL FIX: use shell form so $PORT is read
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
