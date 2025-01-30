from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from .utils.task_processor import stream_results

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://howyoufind.me"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    query: str


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/search-rank/stream")
async def search_rank_stream(request: SearchRequest):
    """Stream search ranking results"""
    return StreamingResponse(
        stream_results(request.query), media_type="text/event-stream"
    )
