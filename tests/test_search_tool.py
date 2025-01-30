import pytest
from unittest.mock import patch, MagicMock
from howdoyoufindme.tools.search_tool import MarketSearchTool


def test_market_search_tool_success():
    with patch('howdoyoufindme.tools.search_tool.BingSearchAPIWrapper') as mock_bing:
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.run.return_value = "Mock search results"
        mock_bing.return_value = mock_instance

        # Create and run tool
        tool = MarketSearchTool()
        result = tool._run("test query")

        # Verify
        assert result == "Mock search results"
        mock_instance.run.assert_called_once_with("test query")


def test_market_search_tool_error():
    with patch('howdoyoufindme.tools.search_tool.BingSearchAPIWrapper') as mock_bing:
        # Setup mock to raise exception
        mock_instance = MagicMock()
        mock_instance.run.side_effect = Exception("API Error")
        mock_bing.return_value = mock_instance

        # Create and run tool
        tool = MarketSearchTool()
        result = tool._run("test query")

        # Verify error handling
        assert "Error performing search" in result
        assert "API Error" in result
        mock_instance.run.assert_called_once_with("test query")