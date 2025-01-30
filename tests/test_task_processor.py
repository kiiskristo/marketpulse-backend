import json
from unittest.mock import MagicMock, patch

import pytest

from howdoyoufindme.utils.task_processor import stream_results


@pytest.mark.asyncio
async def test_stream_results_success(
    mock_crew, sample_keyword_response, sample_ranking_response
):
    # Mock the crew execution
    mock_crew_instance = MagicMock()
    mock_crew_execution = MagicMock()
    
    # Setup the mock crew execution results
    mock_crew_execution.execute_task = MagicMock(side_effect=[
        MagicMock(raw=json.dumps(sample_keyword_response)),  # keywords task
        MagicMock(raw=json.dumps({"queries": ["test query"]})),  # query task
        MagicMock(raw=json.dumps(sample_ranking_response))  # ranking task
    ])
    
    # Setup the crew instance to return our mock execution
    mock_crew_instance.crew.return_value = mock_crew_execution

    with patch(
        "howdoyoufindme.utils.task_processor.HowDoYouFindMeCrew",
        return_value=mock_crew_instance
    ):
        events = []
        async for event in stream_results("test company", use_sse_format=False):
            events.append(json.loads(event.strip()))

        # Verify event sequence
        assert events[0]["type"] == "status"
        assert events[0]["message"] == "Starting analysis..."

        # Find task_complete events
        task_complete_events = [e for e in events if e["type"] == "task_complete"]
        assert len(task_complete_events) >= 2  # At least keywords and ranking results

        # Verify final complete event
        assert events[-1]["type"] == "complete"
        assert events[-1]["message"] == "Analysis complete"


@pytest.mark.asyncio
async def test_stream_results_error():
    # Mock crew instance and execution
    mock_crew_instance = MagicMock()
    mock_crew_execution = MagicMock()
    
    # Setup error
    mock_crew_execution.execute_task = MagicMock(
        side_effect=Exception("Test error")
    )
    mock_crew_instance.crew.return_value = mock_crew_execution

    with patch(
        "howdoyoufindme.utils.task_processor.HowDoYouFindMeCrew",
        return_value=mock_crew_instance
    ):
        events = []
        async for event in stream_results("test company", use_sse_format=False):
            events.append(json.loads(event.strip()))

        # Should get an error event
        error_events = [e for e in events if e["type"] == "error"]
        assert len(error_events) > 0
        assert "Error during analysis: Test error" in error_events[0]["message"]


@pytest.mark.asyncio
async def test_stream_results_sse_format():
    """Test that SSE formatting is applied correctly when enabled"""
    # Mock crew instance and execution
    mock_crew_instance = MagicMock()
    mock_crew_execution = MagicMock()
    
    # Setup error
    mock_crew_execution.execute_task = MagicMock(
        side_effect=Exception("Test error")
    )
    mock_crew_instance.crew.return_value = mock_crew_execution

    with patch(
        "howdoyoufindme.utils.task_processor.HowDoYouFindMeCrew",
        return_value=mock_crew_instance
    ):
        events = []
        async for event in stream_results("test company", use_sse_format=True):
            events.append(event)

        # Verify SSE format
        for event in events:
            assert event.startswith("data: ")
            assert event.endswith("\n\n")
            # Verify we can parse the JSON after removing SSE formatting
            data = event.removeprefix("data: ").removesuffix("\n\n")
            parsed = json.loads(data)
            assert isinstance(parsed, dict)
            assert "type" in parsed

        # Verify error is properly formatted as SSE
        error_events = [
            json.loads(e.removeprefix("data: ").removesuffix("\n\n"))
            for e in events
            if "error" in e
        ]
        assert len(error_events) > 0
        assert "Error during analysis: Test error" in error_events[0]["message"]