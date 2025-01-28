#!/bin/sh
PORT="${PORT:-8080}"  # Default to 8080 if PORT not set
exec uvicorn src.howdoyoufindme.main:app --host 0.0.0.0 --port "$PORT"