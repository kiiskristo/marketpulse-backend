# src/howdoyoufindme/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from .utils.task_processor import stream_results

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://howyoufind.me", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "text/event-stream"]
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/search-rank/stream")
async def search_rank_stream(query: str):
    # Set chunked transfer encoding and disable buffering
    return StreamingResponse(
        stream_results(query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable Nginx buffering
            "Transfer-Encoding": "chunked"
        }
    )