# src/howdoyoufindme/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from .utils.task_processor import stream_results
from .flows.search_rank_flow import SearchRankFlow
from typing import AsyncGenerator
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://howyoufind.me", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "text/event-stream"]
)

async def event_generator(query: str) -> AsyncGenerator[str, None]:
    """Generate SSE events from flow"""
    flow = SearchRankFlow(query)
    async for event in flow.stream_analysis():
        yield event
        await asyncio.sleep(0)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/search-rank/stream")
async def search_rank_stream(query: str):
    return StreamingResponse(
        stream_results(query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Transfer-Encoding": "chunked"
        }
    )
    

@app.get("/api/search-rank/flow")
async def search_rank_flow(query: str):
    return StreamingResponse(
        event_generator(query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "X-Accel-Buffering": "no",
            "Transfer-Encoding": "chunked"
        }
    )