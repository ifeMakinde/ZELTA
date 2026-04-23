FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "\
from transformers import pipeline; \
p = pipeline('sentiment-analysis', \
model='cardiffnlp/twitter-roberta-base-sentiment-latest'); \
print('Model ready')"

COPY . .

# Simple clean PYTHONPATH — only zelta_ai root needed
ENV PYTHONPATH=/app/zelta_ai

ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]