# tests/test_search_rank_flow.py

import json
from unittest.mock import patch, MagicMock
import pytest

from howdoyoufindme.flows.search_rank_flow import SearchRankFlow

@pytest.fixture
def mock_crew_result(sample_keyword_response):
    """Create mock crew responses"""
    # Sample responses for each task
    query_response = {
        "queries": ["test query"], 
        "results": ["test result"]
    }
    ranking_response = {
        "ranking_position": "#1",
        "market_context": {"size": "large", "growth": "high"},
        "comparison": ["comp1", "comp2"]
    }

    # Create mock task outputs
    return MagicMock(
        tasks_output=[
            MagicMock(raw=json.dumps(sample_keyword_response)),
            MagicMock(raw=json.dumps(query_response)),
            MagicMock(raw=json.dumps(ranking_response))
        ]
    )

@pytest.mark.asyncio
async def test_search_rank_flow(mock_crew_result):
    with patch('howdoyoufindme.flows.search_rank_flow.HowDoYouFindMeCrew') as MockCrew:
        # Setup mock
        mock_crew = MagicMock()
        mock_crew.crew.return_value.kickoff.return_value = mock_crew_result
        MockCrew.return_value = mock_crew
        
        # Create flow instance
        flow = SearchRankFlow(query="test company")
        
        # Collect all events
        events = []
        async for event in flow.stream_analysis():
            # Remove SSE formatting for easier testing
            event_str = event.removeprefix("data: ").removesuffix("\n\n")
            events.append(json.loads(event_str))
        
        # Verify event sequence
        status_events = [e for e in events if e["type"] == "status"]
        assert len(status_events) == 3  # Initial, queries, ranking
        assert status_events[0]["message"] == "Starting analysis..."
        
        # Find task_complete events
        task_events = [e for e in events if e["type"] == "task_complete"]
        assert len(task_events) == 3
        
        # Verify each task event
        assert task_events[0]["task"] == "keywords"
        assert task_events[1]["task"] == "queries"
        assert task_events[2]["task"] == "ranking"
        
        # Verify data exists in each task event
        for event in task_events:
            assert "data" in event
            assert event["data"] is not None
        
        # Verify final event
        assert events[-1]["type"] == "complete"
        assert events[-1]["message"] == "Analysis complete"

@pytest.mark.asyncio
async def test_search_rank_flow_error():
    with patch('howdoyoufindme.flows.search_rank_flow.HowDoYouFindMeCrew') as MockCrew:
        mock_crew = MagicMock()
        mock_crew.crew.return_value.kickoff.side_effect = Exception("Test error")
        MockCrew.return_value = mock_crew
        
        flow = SearchRankFlow(query="test company")
        
        events = []
        async for event in flow.stream_analysis():
            event_str = event.removeprefix("data: ").removesuffix("\n\n")
            events.append(json.loads(event_str))
        
        # Should get an error event
        error_events = [e for e in events if e["type"] == "error"]
        assert len(error_events) == 1
        assert "Test error" in error_events[0]["message"]