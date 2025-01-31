# tests/test_search_rank_flow.py

import json
from unittest.mock import patch, MagicMock
import pytest
from crewai import Agent, Task, Process

from howdoyoufindme.flows.search_rank_flow import SearchRankFlow

@pytest.fixture
def mock_agent():
    """Create a mock agent"""
    return Agent(
        role="Test Agent",
        goal="Test Goal",
        backstory="Test Backstory"
    )

@pytest.fixture
def mock_task():
    """Create a mock task"""
    return Task(
        description="Test description",
        expected_output="Test output"
    )

@pytest.fixture
def sample_task_responses():
    """Sample responses for each task"""
    return {
        "keywords": {
            "category": "E-commerce",
            "competitors": ["Amazon", "Walmart", "Target"],
            "keywords": ["online retail", "e-commerce", "marketplace"]
        },
        "queries": {
            "queries": ["test query"], 
            "results": ["test result"]
        },
        "ranking": {
            "ranking_position": "#1",
            "market_context": {"size": "large", "growth": "high"},
            "comparison": ["comp1", "comp2"]
        }
    }

@pytest.fixture
def mock_tasks_output(sample_task_responses):
    """Create mock task outputs"""
    return [
        MagicMock(raw=json.dumps(sample_task_responses["keywords"])),
        MagicMock(raw=json.dumps(sample_task_responses["queries"])),
        MagicMock(raw=json.dumps(sample_task_responses["ranking"]))
    ]

@pytest.fixture
def mock_keyword_crew(mock_tasks_output):
    """Create mock keyword crew"""
    mock = MagicMock()
    mock.kickoff = MagicMock(return_value=MagicMock(tasks_output=[mock_tasks_output[0]]))
    return mock

@pytest.fixture
def mock_query_crew(mock_tasks_output):
    """Create mock query crew"""
    mock = MagicMock()
    mock.kickoff = MagicMock(return_value=MagicMock(tasks_output=[mock_tasks_output[1]]))
    return mock

@pytest.fixture
def mock_ranking_crew(mock_tasks_output):
    """Create mock ranking crew"""
    mock = MagicMock()
    mock.kickoff = MagicMock(return_value=MagicMock(tasks_output=[mock_tasks_output[2]]))
    return mock

@pytest.mark.asyncio
async def test_search_rank_flow(mock_agent, mock_task, mock_keyword_crew, mock_query_crew, mock_ranking_crew):
    with patch('howdoyoufindme.flows.search_rank_flow.HowDoYouFindMeCrew') as MockCrew:
        # Setup mock crew instance
        mock_crew_instance = MagicMock()
        mock_crew_instance.keyword_agent.return_value = mock_agent
        mock_crew_instance.query_builder_agent.return_value = mock_agent
        mock_crew_instance.ranking_agent.return_value = mock_agent
        mock_crew_instance.generate_keywords_task.return_value = mock_task
        mock_crew_instance.build_query_task.return_value = mock_task
        mock_crew_instance.ranking_task.return_value = mock_task
        MockCrew.return_value = mock_crew_instance

        # Patch Crew constructor
        with patch('howdoyoufindme.flows.search_rank_flow.Crew') as MockCrewClass:
            MockCrewClass.side_effect = [mock_keyword_crew, mock_query_crew, mock_ranking_crew]
            
            # Create flow instance
            flow = SearchRankFlow(query="test company")
            
            # Collect all events
            events = []
            async for event in flow.stream_analysis():
                event_str = event.removeprefix("data: ").removesuffix("\n\n")
                events.append(json.loads(event_str))

            # Expected event sequence
            expected_sequence = [
                ("status", "Starting analysis..."),
                ("task_complete", "keywords"),
                ("status", "Analyzing queries..."),
                ("task_complete", "queries"),
                ("status", "Determining ranking..."),
                ("task_complete", "ranking"),
                ("complete", "Analysis complete")
            ]

            assert len(events) == len(expected_sequence), f"Got events: {json.dumps(events, indent=2)}"
            
            for i, (expected_type, expected_msg_or_task) in enumerate(expected_sequence):
                assert events[i]["type"] == expected_type, f"Event {i} type mismatch"
                if expected_type == "status":
                    assert events[i]["message"] == expected_msg_or_task
                elif expected_type == "task_complete":
                    assert events[i]["task"] == expected_msg_or_task
                    assert "data" in events[i]
                elif expected_type == "complete":
                    assert events[i]["message"] == expected_msg_or_task

@pytest.mark.asyncio
async def test_search_rank_flow_error(mock_agent, mock_task):
    with patch('howdoyoufindme.flows.search_rank_flow.HowDoYouFindMeCrew') as MockCrew:
        # Setup mock crew instance
        mock_crew_instance = MagicMock()
        mock_crew_instance.keyword_agent.return_value = mock_agent
        mock_crew_instance.query_builder_agent.return_value = mock_agent
        mock_crew_instance.ranking_agent.return_value = mock_agent
        mock_crew_instance.generate_keywords_task.return_value = mock_task
        mock_crew_instance.build_query_task.return_value = mock_task
        mock_crew_instance.ranking_task.return_value = mock_task
        MockCrew.return_value = mock_crew_instance

        # Patch Crew constructor with error
        with patch('howdoyoufindme.flows.search_rank_flow.Crew') as MockCrewClass:
            mock_error_crew = MagicMock()
            mock_error_crew.kickoff = MagicMock(side_effect=Exception("Failed to process keywords data"))
            MockCrewClass.return_value = mock_error_crew
            
            # Create flow instance
            flow = SearchRankFlow(query="test company")
            
            # Collect events
            events = []
            async for event in flow.stream_analysis():
                event_str = event.removeprefix("data: ").removesuffix("\n\n")
                events.append(json.loads(event_str))

            # Should get initial status and error
            assert len(events) == 2, f"Got events: {json.dumps(events, indent=2)}"
            assert events[0]["type"] == "status"
            assert events[1]["type"] == "error"
            assert "Failed to process keywords data" in events[1]["message"]