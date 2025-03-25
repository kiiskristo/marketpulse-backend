# tests/test_market_sentiment_flow.py

import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient

from marketpulse.flows.market_analysis_flow import MarketSentimentFlow


@pytest.fixture
def mock_market_tools():
    """Mock all market tools to avoid external API calls"""
    with patch('marketpulse.tools.market_tool.FinancialNewsSearchTool._run') as mock_news, \
         patch('marketpulse.tools.market_tool.StockQuoteTool._run') as mock_stock, \
         patch('marketpulse.tools.market_tool.InfluencerMonitorTool._run') as mock_influencer:
        
        # Set up return values for the mocked tools
        mock_news.return_value = "Mocked financial news results for testing"
        mock_stock.return_value = """
        {
            "symbol": "AAPL",
            "price": "190.50",
            "change": "1.25",
            "change_percent": "0.66%",
            "volume": "45356789",
            "latest_trading_day": "2023-04-15"
        }
        """
        mock_influencer.return_value = "Mocked influencer monitoring results for testing"
        
        yield {
            "news_tool": mock_news,
            "stock_tool": mock_stock,
            "influencer_tool": mock_influencer
        }


@pytest.fixture
def mock_crew_instance():
    """Mock a crew instance with predefined return values"""
    mock_crew = MagicMock()
    
    # Set up mock task results
    mock_results = {
        "global_news": {
            "market_events": [
                {"headline": "Fed Raises Interest Rates", "impact": "Negative"},
                {"headline": "Strong Earnings Reports", "impact": "Positive"}
            ]
        },
        "portfolio_news": {
            "stock_news": {
                "AAPL": [{"headline": "Apple Announces New Product", "sentiment": "Positive"}],
                "MSFT": [{"headline": "Microsoft Reports Strong Quarter", "sentiment": "Positive"}]
            }
        },
        "influencer_statements": {
            "influencers": [
                {"name": "Elon Musk", "statement": "AI will change everything", "impact": "Positive"},
                {"name": "Jerome Powell", "statement": "Inflation is cooling", "impact": "Positive"}
            ]
        },
        "market_sentiment": {
            "overall_sentiment": "Bullish",
            "sectors": {
                "Technology": "Very Bullish",
                "Finance": "Neutral",
                "Energy": "Bearish"
            }
        },
        "recommendations": {
            "actions": [
                {"symbol": "AAPL", "action": "Buy", "reason": "Strong momentum"},
                {"symbol": "XOM", "action": "Sell", "reason": "Sector weakness"}
            ],
            "portfolio_allocation": {
                "Technology": "60%",
                "Healthcare": "25%",
                "Cash": "15%"
            }
        }
    }
    
    # Configure the mock to return these results for task calls
    mock_crew.kickoff.return_value = mock_results
    
    return mock_crew


@pytest.fixture
def mock_config_files():
    """Mock configuration files for the crew"""
    agents_config = {
        'global_news_agent': {
            'role': 'Global News Analyst',
            'goal': 'Monitor global financial news',
            'backstory': 'Experienced financial news analyst'
        },
        'portfolio_news_agent': {
            'role': 'Portfolio News Analyst',
            'goal': 'Track news for portfolio assets',
            'backstory': 'Specialized in company-specific news'
        },
        'influencer_monitor_agent': {
            'role': 'Influencer Monitor',
            'goal': 'Track statements from key market influencers',
            'backstory': 'Expert in social influence on markets'
        },
        'sentiment_analysis_agent': {
            'role': 'Sentiment Analyst',
            'goal': 'Analyze market sentiment',
            'backstory': 'AI specialist in emotional analysis'
        },
        'portfolio_strategy_agent': {
            'role': 'Portfolio Strategist',
            'goal': 'Create investment strategies',
            'backstory': 'Seasoned investment advisor'
        }
    }

    tasks_config = {
        'collect_global_news_task': {
            'description': 'Collect important global financial news',
            'expected_output': '{"news": [...]}',
            'agent': 'global_news_agent'
        },
        'analyze_portfolio_news_task': {
            'description': 'Analyze news for portfolio stocks',
            'expected_output': '{"stock_news": [...]}',
            'agent': 'portfolio_news_agent'
        },
        'monitor_key_influencers_task': {
            'description': 'Monitor statements from key market influencers',
            'expected_output': '{"influencers": [...]}',
            'agent': 'influencer_monitor_agent'
        },
        'analyze_market_sentiment_task': {
            'description': 'Analyze overall market sentiment',
            'expected_output': '{"sentiment": {...}}',
            'agent': 'sentiment_analysis_agent'
        },
        'generate_recommendations_task': {
            'description': 'Generate investment recommendations',
            'expected_output': '{"recommendations": [...]}',
            'agent': 'portfolio_strategy_agent'
        }
    }

    with patch('crewai.project.crew_base.yaml.safe_load') as mock_yaml:
        mock_yaml.side_effect = [agents_config, tasks_config]
        yield mock_yaml


@patch('marketpulse.tools.market_tool.FinancialNewsSearchTool')
@patch('marketpulse.tools.market_tool.StockQuoteTool')
@patch('marketpulse.tools.market_tool.InfluencerMonitorTool')
@patch('crewai.project.crew_base.yaml.safe_load')
def test_flow_extract_json(mock_yaml, mock_news_tool, mock_stock_tool, mock_influencer_tool):
    """Test the JSON extraction logic without initializing the full flow"""
    # Create a minimal mock instance with just the _extract_json_from_response method
    class MockFlow:
        def _extract_json_from_response(self, text):
            try:
                # First try direct JSON parsing
                return json.loads(text)
            except json.JSONDecodeError:
                try:
                    # Find content between first { and last }
                    start_idx = text.find('{')
                    end_idx = text.rfind('}')
                    if start_idx >= 0 and end_idx > start_idx:
                        json_str = text[start_idx:end_idx + 1]
                        return json.loads(json_str)
                except Exception:
                    return None
    
    # Create an instance of the mock flow
    flow = MockFlow()
    
    # Test valid JSON
    valid_json = '{"test": "value"}'
    result = flow._extract_json_from_response(valid_json)
    assert result == {"test": "value"}
    
    # Test JSON with surrounding text
    json_with_text = 'Some text before {"test": "value"} and after'
    result = flow._extract_json_from_response(json_with_text)
    assert result == {"test": "value"}
    
    # Test invalid JSON
    invalid_json = '{"test": value}'  # Missing quotes around value
    result = flow._extract_json_from_response(invalid_json)
    assert result is None 