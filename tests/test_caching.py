# tests/test_caching.py

import pytest
import os
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import time
from marketpulse.tools.market_tool import (
    FinancialNewsSearchTool,
    StockQuoteTool,
    InfluencerMonitorTool
)


@pytest.fixture
def setup_cache_dirs():
    """Setup and cleanup cache directories for testing"""
    # Create test cache directories
    cache_dirs = [
        ".cache/news",
        ".cache/quotes",
        ".cache/influencers"
    ]
    
    for cache_dir in cache_dirs:
        os.makedirs(cache_dir, exist_ok=True)
    
    os.makedirs(".logs", exist_ok=True)
    
    yield
    
    # Cleanup test cache files
    test_files = [
        ".cache/news/integration_test_query.json",
        ".cache/news/first_query.json",
        ".cache/news/second_query.json",
        ".cache/news/error_query.json",
        ".cache/quotes/TSLA.json",
        ".cache/influencers/jerome_powell.json"
    ]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)


@pytest.fixture
def mock_bing_wrapper():
    """Mock BingSearchAPIWrapper to avoid actual API calls"""
    with patch('langchain_community.utilities.BingSearchAPIWrapper') as mock:
        mock_instance = MagicMock()
        mock_instance.run.return_value = "Mocked search results from Bing API"
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_requests_get():
    """Mock requests.get to avoid actual API calls to Alpha Vantage"""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Global Quote": {
                "01. symbol": "TSLA",
                "05. price": "245.50",
                "09. change": "3.25",
                "10. change percent": "1.34%",
                "06. volume": "35789456",
                "07. latest trading day": "2023-04-15"
            }
        }
        mock_get.return_value = mock_response
        yield mock_get


class TestToolCaching:
    """Integration tests for caching behavior across all tools"""
    
    def test_news_tool_cache_reuse(self, setup_cache_dirs):
        """Test that the news tool properly reuses cache"""
        # Mock BingSearchAPIWrapper constructor
        with patch('marketpulse.tools.market_tool.BingSearchAPIWrapper') as mock_bing_class:
            # Create a mock for the run method
            mock_run = MagicMock(return_value="Mocked search results from Bing")
            
            # The constructor returns an instance with the mocked run method
            mock_bing_instance = MagicMock()
            mock_bing_instance.run = mock_run
            mock_bing_class.return_value = mock_bing_instance
            
            tool = FinancialNewsSearchTool()
            
            # First call - should hit the API
            result1 = tool._run("integration test query")
            assert mock_run.call_count == 1
            assert result1 == "Mocked search results from Bing"
            
            # Second call - should use cache
            result2 = tool._run("integration test query")
            assert mock_run.call_count == 1  # Still just 1 call
            assert result2 == "Mocked search results from Bing"
            
            # Verify log file was created
            assert os.path.exists(".logs/bing_usage.log")
    
    def test_stock_tool_cache_reuse(self, setup_cache_dirs):
        """Test that the stock tool properly reuses cache"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "Global Quote": {
                    "01. symbol": "TSLA",
                    "05. price": "245.50",
                    "09. change": "3.25",
                    "10. change percent": "1.34%",
                    "06. volume": "35789456",
                    "07. latest trading day": "2023-04-15"
                }
            }
            mock_get.return_value = mock_response
            
            tool = StockQuoteTool()
            
            # First call - should hit the API
            result1 = tool._run("TSLA")
            assert mock_get.call_count == 1
            result1_json = json.loads(result1)
            assert result1_json["symbol"] == "TSLA"
            
            # Second call - should use cache
            result2 = tool._run("TSLA")
            assert mock_get.call_count == 1  # Still just 1 call
            
            # Verify log file was created
            assert os.path.exists(".logs/alphavantage_usage.log")
    
    def test_influencer_tool_cache_reuse(self, setup_cache_dirs):
        """Test that the influencer tool properly reuses cache"""
        # Mock BingSearchAPIWrapper constructor
        with patch('marketpulse.tools.market_tool.BingSearchAPIWrapper') as mock_bing_class:
            # Create a mock for the run method
            mock_run = MagicMock(return_value="Mocked search results from Bing")
            
            # The constructor returns an instance with the mocked run method
            mock_bing_instance = MagicMock()
            mock_bing_instance.run = mock_run
            mock_bing_class.return_value = mock_bing_instance
            
            tool = InfluencerMonitorTool()
            
            # First call - should hit the API
            result1 = tool._run("Jerome Powell")
            assert mock_run.call_count == 1
            assert result1 == "Mocked search results from Bing"
            
            # Second call - should use cache
            result2 = tool._run("Jerome Powell")
            assert mock_run.call_count == 1  # Still just 1 call
            assert result2 == "Mocked search results from Bing"
            
            # Verify log file was created
            assert os.path.exists(".logs/bing_usage.log")
    
    def test_cache_expiry(self, setup_cache_dirs):
        """Test that cache properly expires after the designated time"""
        # Mock BingSearchAPIWrapper constructor
        with patch('marketpulse.tools.market_tool.BingSearchAPIWrapper') as mock_bing_class:
            # Create a mock for the run method
            mock_run = MagicMock(return_value="Mocked search results from Bing")
            
            # The constructor returns an instance with the mocked run method
            mock_bing_instance = MagicMock()
            mock_bing_instance.run = mock_run
            mock_bing_class.return_value = mock_bing_instance
            
            tool = FinancialNewsSearchTool()
            
            # Create a cache file with yesterday's date
            cache_file = ".cache/news/integration_test_query.json"
            with open(cache_file, 'w') as f:
                f.write("Old cached results")
            
            # Set the modification time to yesterday
            yesterday = datetime.now() - timedelta(days=1)
            os.utime(cache_file, (yesterday.timestamp(), yesterday.timestamp()))
            
            # This should ignore the old cache and make a new API call
            result = tool._run("integration test query")
            assert mock_run.call_count == 1
            assert result == "Mocked search results from Bing"
            
            # Verify the cache was updated
            with open(cache_file, 'r') as f:
                assert f.read() == "Mocked search results from Bing"
    
    def test_multiple_queries_caching(self, setup_cache_dirs):
        """Test that different queries are cached separately"""
        # Mock BingSearchAPIWrapper constructor
        with patch('marketpulse.tools.market_tool.BingSearchAPIWrapper') as mock_bing_class:
            # Create a mock for the run method
            mock_run = MagicMock(return_value="Mocked search results from Bing")
            
            # The constructor returns an instance with the mocked run method
            mock_bing_instance = MagicMock()
            mock_bing_instance.run = mock_run
            mock_bing_class.return_value = mock_bing_instance
            
            tool = FinancialNewsSearchTool()
            
            # First query
            result1 = tool._run("first query")
            
            # Second query - should make a new API call
            result2 = tool._run("second query")
            
            # Both should have made API calls
            assert mock_run.call_count == 2
            
            # Cache files should exist for both
            assert os.path.exists(".cache/news/first_query.json")
            assert os.path.exists(".cache/news/second_query.json")
            
            # Calling first query again should use cache
            tool._run("first query")
            assert mock_run.call_count == 2  # No new calls
    
    def test_cache_creation_on_error(self, setup_cache_dirs):
        """Test that failed API calls don't create cache files"""
        # Mock BingSearchAPIWrapper constructor
        with patch('marketpulse.tools.market_tool.BingSearchAPIWrapper') as mock_bing_class:
            # Create a mock that raises an exception
            mock_run = MagicMock(side_effect=Exception("API Error"))
            
            # The constructor returns an instance with the mocked run method
            mock_bing_instance = MagicMock()
            mock_bing_instance.run = mock_run
            mock_bing_class.return_value = mock_bing_instance
            
            tool = FinancialNewsSearchTool()
            
            # Should return an error message when API call fails
            result = tool._run("error query")
            assert "Error performing search" in result
            
            # No cache file should be created on error
            assert not os.path.exists(".cache/news/error_query.json") 