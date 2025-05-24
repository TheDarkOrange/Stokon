# Dockerfile for Stokon

FROM python:3.10-slim

# System deps
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/logs

CMD ["bash","-c","python -m src.main"]
