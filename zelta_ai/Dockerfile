# Use Python 3.11 slim
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for torch
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# PRE-DOWNLOAD RoBERTa model during build
# This bakes it into the image so Cloud Run never downloads it
# Without this, Cloud Run times out waiting for 500MB download
RUN python -c "\
from transformers import pipeline; \
print('Downloading RoBERTa model...'); \
p = pipeline('sentiment-analysis', \
model='cardiffnlp/twitter-roberta-base-sentiment-latest'); \
print('Model downloaded successfully')"

# Copy ALL source code
COPY . .

# Cloud Run requires port 8080
ENV PORT=8080
EXPOSE 8080

# Start the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]