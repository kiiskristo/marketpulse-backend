FROM python:3.12-slim

WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src/ ./src/

# Command to run the application
CMD ["sh", "-c", "uvicorn src.howdoyoufindme.main:app --host 0.0.0.0 --port $PORT"]