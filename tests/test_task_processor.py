import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from howdoyoufindme.utils.task_processor import stream_results


@pytest.mark.asyncio
async def test_stream_results_success(
    mock_crew, sample_keyword_response, sample_ranking_response
):
    # Mock the task results
    keywords_task_mock = AsyncMock()
    keywords_task_mock.run_async = AsyncMock(
        return_value=MagicMock(raw=json.dumps(sample_keyword_response))
    )

    query_task_mock = AsyncMock()
    query_task_mock.run_async = AsyncMock(
        return_value=MagicMock(raw=json.dumps({"queries": ["test query"]}))
    )

    ranking_task_mock = AsyncMock()
    ranking_task_mock.run_async = AsyncMock(
        return_value=MagicMock(raw=json.dumps(sample_ranking_response))
    )

    mock_crew.generate_keywords_task.return_value = keywords_task_mock
    mock_crew.build_query_task.return_value = query_task_mock
    mock_crew.ranking_task.return_value = ranking_task_mock

    with patch(
        "howdoyoufindme.utils.task_processor.HowDoYouFindMeCrew", return_value=mock_crew
    ):
        events = []
        # Set use_sse_format=False for testing
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
    # Create a mock crew instance
    mock_crew = AsyncMock()

    # Create a mock task that raises an exception
    error_task = AsyncMock()
    error_task.run_async = AsyncMock(side_effect=Exception("Test error"))

    # Set up the mock crew to return our error task
    mock_crew.generate_keywords_task = MagicMock(return_value=error_task)

    with patch(
        "howdoyoufindme.utils.task_processor.HowDoYouFindMeCrew", return_value=mock_crew
    ):
        events = []
        # Set use_sse_format=False for testing
        async for event in stream_results("test company", use_sse_format=False):
            events.append(json.loads(event.strip()))

        # Should get an error event
        error_events = [e for e in events if e["type"] == "error"]
        assert len(error_events) > 0
        assert "Test error" in error_events[0]["message"]


@pytest.mark.asyncio
async def test_stream_results_sse_format():
    """Test that SSE formatting is applied correctly when enabled"""
    mock_crew = AsyncMock()
    error_task = AsyncMock()
    error_task.run_async = AsyncMock(side_effect=Exception("Test error"))
    mock_crew.generate_keywords_task = MagicMock(return_value=error_task)

    with patch(
        "howdoyoufindme.utils.task_processor.HowDoYouFindMeCrew", return_value=mock_crew
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