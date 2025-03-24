# src/market_sentiment/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from .flows.market_analysis_flow import MarketSentimentFlow
from typing import AsyncGenerator, Dict, Any, List
import asyncio
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "text/event-stream"]
)

class Portfolio(BaseModel):
    """User portfolio model"""
    holdings: List[Dict[str, Any]]
    
class Preferences(BaseModel):
    """User preferences model"""
    risk_tolerance: str
    preferred_sectors: List[str] = []
    preferred_regions: List[str] = []
    investment_horizon: str

class SentimentRequest(BaseModel):
    """Request model for sentiment analysis"""
    portfolio: Portfolio
    preferences: Preferences

async def event_generator(portfolio: Dict[str, Any], preferences: Dict[str, Any]) -> AsyncGenerator[str, None]:
    """Generate SSE events from sentiment analysis flow"""
    flow = MarketSentimentFlow(portfolio, preferences)
    async for event in flow.stream_analysis():
        yield event
        await asyncio.sleep(0)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/sentiment/analyze")
async def analyze_sentiment(request: SentimentRequest):
    """Analyze market sentiment for a user's portfolio"""
    try:
        portfolio_dict = request.portfolio.dict()
        preferences_dict = request.preferences.dict()
        
        return StreamingResponse(
            event_generator(portfolio_dict, preferences_dict),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
                "X-Accel-Buffering": "no",
                "Transfer-Encoding": "chunked"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/api/sentiment/demo")
async def analyze_sentiment_demo():
    """Demo endpoint with sample portfolio data"""
    sample_portfolio = {
        "holdings": [
            {"ticker": "AAPL", "company": "Apple Inc.", "allocation": 15, "sector": "Technology"},
            {"ticker": "MSFT", "company": "Microsoft Corp.", "allocation": 12, "sector": "Technology"},
            {"ticker": "AMZN", "company": "Amazon.com Inc.", "allocation": 10, "sector": "Consumer Discretionary"},
            {"ticker": "GOOGL", "company": "Alphabet Inc.", "allocation": 8, "sector": "Communication Services"},
            {"ticker": "TSLA", "company": "Tesla Inc.", "allocation": 5, "sector": "Consumer Discretionary"}
        ]
    }
    
    sample_preferences = {
        "risk_tolerance": "moderate",
        "preferred_sectors": ["Technology", "Healthcare"],
        "preferred_regions": ["US", "Europe"],
        "investment_horizon": "medium-term"
    }
    
    return StreamingResponse(
        event_generator(sample_portfolio, sample_preferences),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "X-Accel-Buffering": "no",
            "Transfer-Encoding": "chunked"
        }
    )