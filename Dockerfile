# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy only requirements first for better caching
COPY requirements.txt .
COPY pyproject.toml .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir .

# Copy the rest of the code
COPY . .

# Command to run the application
# Railway will inject the PORT environment variable
CMD uvicorn src.howdoyoufindme.main:app --host 0.0.0.0 --port $PORT