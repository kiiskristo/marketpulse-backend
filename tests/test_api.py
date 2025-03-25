# tests/test_api.py

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from marketpulse.main import app

@pytest.fixture
def test_client():
    return TestClient(app)

def test_health_check(test_client):
    """Test the health check endpoint"""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch('marketpulse.main.MarketSentimentFlow')
def test_sentiment_analyze_input_validation(mock_flow, test_client):
    """Test input validation for the sentiment analyze endpoint"""
    # Test with missing required fields
    response = test_client.post("/api/sentiment/analyze", json={})
    assert response.status_code == 422  # FastAPI validation error
    
    # Test with invalid portfolio format
    invalid_data = {
        "portfolio": {"invalid": "data"},
        "preferences": {
            "risk_tolerance": "moderate",
            "investment_horizon": "medium-term"
        }
    }
    response = test_client.post("/api/sentiment/analyze", json=invalid_data)
    assert response.status_code == 422  # Validation error

@patch('marketpulse.main.event_generator')
def test_sentiment_analyze_response_format(mock_generator, test_client):
    """Test the response format for sentiment analyze endpoint"""
    # Create an async generator that returns a single event
    async def mock_event_gen(*args, **kwargs):
        yield "data: test event\n\n"
    
    # Set up the mock
    mock_generator.return_value = mock_event_gen()
    
    # Create valid request data
    data = {
        "portfolio": {
            "holdings": [
                {"ticker": "AAPL", "company": "Apple Inc.", "allocation": 15, "sector": "Technology"}
            ]
        },
        "preferences": {
            "risk_tolerance": "moderate",
            "preferred_sectors": ["Technology"],
            "preferred_regions": ["US"],
            "investment_horizon": "medium-term"
        }
    }
    
    # Test the endpoint
    response = test_client.post("/api/sentiment/analyze", json=data)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream"

@patch('marketpulse.main.event_generator')
def test_sentiment_demo_response_format(mock_generator, test_client):
    """Test the response format for sentiment demo endpoint"""
    # Create an async generator that returns a single event
    async def mock_event_gen(*args, **kwargs):
        yield "data: test event\n\n"
    
    # Set up the mock
    mock_generator.return_value = mock_event_gen()
    
    # Test the endpoint
    response = test_client.get("/api/sentiment/demo")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream"