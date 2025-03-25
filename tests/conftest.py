# tests/conftest.py

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
import os
import json
from datetime import datetime, timedelta

from marketpulse.main import app


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def mock_bing_wrapper():
    with patch('langchain_community.utilities.BingSearchAPIWrapper') as mock:
        mock_instance = MagicMock()
        mock_instance.run.return_value = "Search results"
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_market_data():
    return {
        "market_events": [
            {"headline": "Fed Raises Interest Rates", "impact": "Negative"},
            {"headline": "Strong Earnings Reports", "impact": "Positive"}
        ],
        "stock_news": {
            "AAPL": [{"headline": "Apple Announces New Product", "sentiment": "Positive"}],
            "MSFT": [{"headline": "Microsoft Reports Strong Quarter", "sentiment": "Positive"}]
        }
    }


@pytest.fixture
def sample_sentiment_data():
    return {
        "overall_sentiment": "Bullish",
        "sectors": {
            "Technology": "Very Bullish",
            "Finance": "Neutral",
            "Energy": "Bearish"
        }
    }


@pytest.fixture
def setup_cache_dirs():
    """Setup and cleanup cache directories for testing"""
    # Create test cache directories
    os.makedirs(".cache/news", exist_ok=True)
    os.makedirs(".cache/quotes", exist_ok=True)
    os.makedirs(".cache/influencers", exist_ok=True)
    os.makedirs(".logs", exist_ok=True)
    
    yield
    
    # Cleanup test cache files created during tests
    test_files = [
        ".cache/news/test_query.json",
        ".cache/news/integration_test_query.json",
        ".cache/news/first_query.json",
        ".cache/news/second_query.json",
        ".cache/quotes/AAPL.json",
        ".cache/quotes/TSLA.json",
        ".cache/influencers/elon_musk.json",
        ".cache/influencers/jerome_powell.json"
    ]
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)


@pytest.fixture(autouse=True)
def mock_config_files():
    agents_config = {
        # Original agents for HowDoYouFindMeCrew
        'keyword_agent': {
            'role': 'Industry Category Analyst',
            'goal': 'Identify industry category',
            'backstory': 'Test backstory'
        },
        'query_builder_agent': {
            'role': 'Market Research Expert',
            'goal': 'Research top companies',
            'backstory': 'Test backstory'
        },
        'ranking_agent': {
            'role': 'Competitive Position Analyzer',
            'goal': 'Determine rankings',
            'backstory': 'Test backstory'
        },
        # Agents for MarketSentimentCrew
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
        # Original tasks for HowDoYouFindMeCrew
        'generate_keywords_task': {
            'description': 'Test description',
            'expected_output': '{"test": "output"}',
            'agent': 'keyword_agent'
        },
        'build_query_task': {
            'description': 'Test description',
            'expected_output': '{"test": "output"}',
            'agent': 'query_builder_agent'
        },
        'ranking_task': {
            'description': 'Test description',
            'expected_output': '{"test": "output"}',
            'agent': 'ranking_agent'
        },
        # Tasks for MarketSentimentCrew
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


@pytest.fixture
def mock_task_outputs():
    """Mock outputs for various tasks"""
    mock_outputs = {}
    
    # Global news task output
    mock_outputs["global_news"] = MagicMock()
    mock_outputs["global_news"].raw = json.dumps({
        "market_events": [
            {"headline": "Fed Raises Interest Rates", "impact": "Negative"},
            {"headline": "Strong Earnings Reports", "impact": "Positive"}
        ]
    })
    
    # Portfolio news task output
    mock_outputs["portfolio_news"] = MagicMock()
    mock_outputs["portfolio_news"].raw = json.dumps({
        "stock_news": {
            "AAPL": [{"headline": "Apple Announces New Product", "sentiment": "Positive"}],
            "MSFT": [{"headline": "Microsoft Reports Strong Quarter", "sentiment": "Positive"}]
        }
    })
    
    # Influencer task output
    mock_outputs["influencer"] = MagicMock()
    mock_outputs["influencer"].raw = json.dumps({
        "influencers": [
            {"name": "Elon Musk", "statement": "AI will change everything", "impact": "Positive"},
            {"name": "Jerome Powell", "statement": "Inflation is cooling", "impact": "Positive"}
        ]
    })
    
    # Sentiment analysis task output
    mock_outputs["sentiment"] = MagicMock()
    mock_outputs["sentiment"].raw = json.dumps({
        "sentiment": {
            "overall_sentiment": "Bullish",
            "sectors": {
                "Technology": "Very Bullish",
                "Finance": "Neutral",
                "Energy": "Bearish"
            }
        }
    })
    
    # Recommendations task output
    mock_outputs["recommendations"] = MagicMock()
    mock_outputs["recommendations"].raw = json.dumps({
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
    })
    
    return mock_outputs


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


@pytest.fixture(scope="function")
def mock_env():
    """Mock environment variables"""
    with patch.dict(os.environ, {"MODEL": "gpt-3.5-turbo"}):
        yield