FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

# Use CMD with direct command and shell form to ensure environment variable expansion
CMD uvicorn src.howdoyoufindme.main:app --host 0.0.0.0 --port 8080