# tests/test_market_tools.py

import pytest
import os
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from marketpulse.tools.market_tool import (
    FinancialNewsSearchTool,
    StockQuoteTool,
    InfluencerMonitorTool,
    NewsSearchInput,
    StockQuoteInput,
    InfluencerMonitorInput
)


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
        ".cache/quotes/AAPL.json",
        ".cache/influencers/elon_musk.json"
    ]
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)


class TestFinancialNewsSearchTool:
    
    def test_initialization(self):
        """Test that the tool initializes correctly with Bing wrapper"""
        with patch('marketpulse.tools.market_tool.BingSearchAPIWrapper'):
            tool = FinancialNewsSearchTool()
            assert tool.name == "financial_news_search"
            assert tool.bing_search is not None
            assert "financial and economic news" in tool.description
    
    def test_run_with_no_cache(self, setup_cache_dirs):
        """Test tool execution when no cache exists"""
        # Remove cache file if it exists
        cache_file = ".cache/news/test_query.json"
        if os.path.exists(cache_file):
            os.remove(cache_file)
        
        # Mock BingSearchAPIWrapper constructor
        with patch('marketpulse.tools.market_tool.BingSearchAPIWrapper') as mock_bing_class:
            # Create a mock for the run method
            mock_run = MagicMock(return_value="Mocked search results from Bing")
            
            # The constructor returns an instance with the mocked run method
            mock_bing_instance = MagicMock()
            mock_bing_instance.run = mock_run
            mock_bing_class.return_value = mock_bing_instance
            
            # Create the tool which will use our mocked BingSearchAPIWrapper
            tool = FinancialNewsSearchTool()
            result = tool._run("test query")
            
            # Verify API was called
            mock_run.assert_called_once_with("financial news test query")
            
            # Verify result is correct
            assert result == "Mocked search results from Bing"
            
            # Verify cache was created
            assert os.path.exists(cache_file)
    
    def test_run_with_existing_cache(self, setup_cache_dirs):
        """Test tool execution when cache exists"""
        # Create a cache file
        cache_file = ".cache/news/test_query.json"
        with open(cache_file, 'w') as f:
            f.write("Cached test results")
        
        # Set modification time to today
        os.utime(cache_file, (datetime.now().timestamp(), datetime.now().timestamp()))
        
        # Mock BingSearchAPIWrapper constructor
        with patch('marketpulse.tools.market_tool.BingSearchAPIWrapper') as mock_bing_class:
            # Create a mock for the run method
            mock_run = MagicMock(return_value="These results should not be returned")
            
            # The constructor returns an instance with the mocked run method
            mock_bing_instance = MagicMock()
            mock_bing_instance.run = mock_run
            mock_bing_class.return_value = mock_bing_instance
            
            # Create the tool which will use our mocked BingSearchAPIWrapper
            tool = FinancialNewsSearchTool()
            result = tool._run("test query")
            
            # Verify API was NOT called
            mock_run.assert_not_called()
            
            # Verify cached result is returned
            assert result == "Cached test results"
    
    def test_run_with_old_cache(self, setup_cache_dirs):
        """Test tool execution when cache is old (from yesterday)"""
        # Create a cache file
        cache_file = ".cache/news/test_query.json"
        with open(cache_file, 'w') as f:
            f.write("Cached test results")
        
        # Set modification time to yesterday
        yesterday = datetime.now() - timedelta(days=1)
        os.utime(cache_file, (yesterday.timestamp(), yesterday.timestamp()))
        
        # Mock BingSearchAPIWrapper constructor
        with patch('marketpulse.tools.market_tool.BingSearchAPIWrapper') as mock_bing_class:
            # Create a mock for the run method
            mock_run = MagicMock(return_value="Mocked search results from Bing")
            
            # The constructor returns an instance with the mocked run method
            mock_bing_instance = MagicMock()
            mock_bing_instance.run = mock_run
            mock_bing_class.return_value = mock_bing_instance
            
            # Create the tool which will use our mocked BingSearchAPIWrapper
            tool = FinancialNewsSearchTool()
            result = tool._run("test query")
            
            # Verify API was called (because cache is old)
            mock_run.assert_called_once_with("financial news test query")
            
            # Verify result is from API, not cache
            assert result == "Mocked search results from Bing"


class TestStockQuoteTool:
    
    def test_initialization(self):
        """Test that the tool initializes correctly"""
        tool = StockQuoteTool()
        assert tool.name == "stock_quote"
        assert "current stock price data" in tool.description
    
    def test_run_with_no_cache(self, setup_cache_dirs):
        """Test tool execution when no cache exists"""
        # Remove cache file if it exists
        cache_file = ".cache/quotes/AAPL.json"
        if os.path.exists(cache_file):
            os.remove(cache_file)
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "Global Quote": {
                    "01. symbol": "AAPL",
                    "05. price": "190.50",
                    "09. change": "1.25",
                    "10. change percent": "0.66%",
                    "06. volume": "45356789",
                    "07. latest trading day": "2023-04-15"
                }
            }
            mock_get.return_value = mock_response
            
            tool = StockQuoteTool()
            result = tool._run("AAPL")
            
            # Parse the result to verify it's JSON
            result_json = json.loads(result)
            
            # Verify API was called
            mock_get.assert_called_once()
            
            # Verify result is correct
            assert result_json["symbol"] == "AAPL"
            assert result_json["price"] == "190.50"
            
            # Verify cache was created
            assert os.path.exists(cache_file)
    
    def test_run_with_existing_cache(self, setup_cache_dirs):
        """Test tool execution when cache exists and is recent"""
        # Create a cache file
        cache_file = ".cache/quotes/AAPL.json"
        cache_data = {
            "symbol": "AAPL",
            "price": "191.50",  # Different from mock API to verify we get cache
            "change": "1.50",
            "change_percent": "0.79%",
            "volume": "45000000",
            "latest_trading_day": "2023-04-15"
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        # Set modification time to 30 minutes ago (within the 1 hour threshold)
        thirty_min_ago = datetime.now() - timedelta(minutes=30)
        os.utime(cache_file, (thirty_min_ago.timestamp(), thirty_min_ago.timestamp()))
        
        with patch('requests.get') as mock_get:
            tool = StockQuoteTool()
            result = tool._run("AAPL")
            
            # Parse the result to verify it's JSON
            result_json = json.loads(result)
            
            # Verify API was NOT called (because cache is recent)
            mock_get.assert_not_called()
            
            # Verify cached result is returned (the price we set differs from the mock API)
            assert result_json["price"] == "191.50"


class TestInfluencerMonitorTool:
    
    def test_initialization(self):
        """Test that the tool initializes correctly with Bing wrapper"""
        with patch('marketpulse.tools.market_tool.BingSearchAPIWrapper'):
            tool = InfluencerMonitorTool()
            assert tool.name == "influencer_monitor"
            assert tool.bing_search is not None
            assert "key market influencers" in tool.description
    
    def test_run_with_no_cache(self, setup_cache_dirs):
        """Test tool execution when no cache exists"""
        # Remove cache file if it exists
        cache_file = ".cache/influencers/elon_musk.json"
        if os.path.exists(cache_file):
            os.remove(cache_file)
        
        # Mock BingSearchAPIWrapper constructor
        with patch('marketpulse.tools.market_tool.BingSearchAPIWrapper') as mock_bing_class:
            # Create a mock for the run method
            mock_run = MagicMock(return_value="Mocked search results from Bing")
            
            # The constructor returns an instance with the mocked run method
            mock_bing_instance = MagicMock()
            mock_bing_instance.run = mock_run
            mock_bing_class.return_value = mock_bing_instance
            
            # Create the tool which will use our mocked BingSearchAPIWrapper
            tool = InfluencerMonitorTool()
            result = tool._run("Elon Musk")
            
            # Verify API was called with proper query formatting
            expected_query = "Elon Musk recent statement market finance economy (site:cnbc.com OR site:bloomberg.com OR site:reuters.com OR site:ft.com OR site:wsj.com)"
            mock_run.assert_called_once_with(expected_query)
            
            # Verify result is correct
            assert result == "Mocked search results from Bing"
            
            # Verify cache was created
            assert os.path.exists(cache_file)
    
    def test_run_with_existing_cache(self, setup_cache_dirs):
        """Test tool execution when cache exists and is recent"""
        # Create a cache file
        cache_file = ".cache/influencers/elon_musk.json"
        with open(cache_file, 'w') as f:
            f.write("Cached Elon Musk results")
        
        # Set modification time to 2 hours ago (within the 4 hour threshold)
        two_hours_ago = datetime.now() - timedelta(hours=2)
        os.utime(cache_file, (two_hours_ago.timestamp(), two_hours_ago.timestamp()))
        
        # Mock BingSearchAPIWrapper constructor
        with patch('marketpulse.tools.market_tool.BingSearchAPIWrapper') as mock_bing_class:
            # Create a mock for the run method
            mock_run = MagicMock(return_value="These results should not be returned")
            
            # The constructor returns an instance with the mocked run method
            mock_bing_instance = MagicMock()
            mock_bing_instance.run = mock_run
            mock_bing_class.return_value = mock_bing_instance
            
            # Create the tool which will use our mocked BingSearchAPIWrapper
            tool = InfluencerMonitorTool()
            result = tool._run("Elon Musk")
            
            # Verify API was NOT called
            mock_run.assert_not_called()
            
            # Verify cached result is returned
            assert result == "Cached Elon Musk results"
    
    def test_run_with_old_cache(self, setup_cache_dirs):
        """Test tool execution when cache is old (more than 4 hours)"""
        # Create a cache file
        cache_file = ".cache/influencers/elon_musk.json"
        with open(cache_file, 'w') as f:
            f.write("Cached Elon Musk results")
        
        # Set modification time to 5 hours ago (beyond the 4 hour threshold)
        five_hours_ago = datetime.now() - timedelta(hours=5)
        os.utime(cache_file, (five_hours_ago.timestamp(), five_hours_ago.timestamp()))
        
        # Mock BingSearchAPIWrapper constructor
        with patch('marketpulse.tools.market_tool.BingSearchAPIWrapper') as mock_bing_class:
            # Create a mock for the run method
            mock_run = MagicMock(return_value="Mocked search results from Bing")
            
            # The constructor returns an instance with the mocked run method
            mock_bing_instance = MagicMock()
            mock_bing_instance.run = mock_run
            mock_bing_class.return_value = mock_bing_instance
            
            # Create the tool which will use our mocked BingSearchAPIWrapper
            tool = InfluencerMonitorTool()
            result = tool._run("Elon Musk")
            
            # Verify API was called (because cache is old)
            expected_query = "Elon Musk recent statement market finance economy (site:cnbc.com OR site:bloomberg.com OR site:reuters.com OR site:ft.com OR site:wsj.com)"
            mock_run.assert_called_once_with(expected_query)
            
            # Verify result is from API, not cache
            assert result == "Mocked search results from Bing" 