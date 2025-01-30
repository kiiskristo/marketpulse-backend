import json
from unittest.mock import patch

import pytest


def test_health_check(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_search_rank_stream(
    test_client, mock_crew, sample_keyword_response, sample_ranking_response
):
    # Mock the streaming response
    async def mock_stream():
        yield b'{"type":"status","message":"Starting..."}\n'
        # Properly serialize the dictionary to JSON
        keyword_data = json.dumps(
            {
                "type": "task_complete",
                "task": "keywords",
                "data": sample_keyword_response,
            }
        )
        yield (keyword_data + "\n").encode()
        yield b'{"type":"complete","message":"Analysis complete"}\n'

    with patch("howdoyoufindme.main.stream_results", return_value=mock_stream()):
        response = test_client.post(
            "/api/search-rank/stream", json={"query": "test company"}
        )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")

        # Read all response content
        content = response.content
        events = [json.loads(line) for line in content.decode().split("\n") if line]

        # Check first event
        assert events[0]["type"] == "status"
        assert events[0]["message"] == "Starting..."

        # Check the keywords event
        keywords_event = next(
            (
                e
                for e in events
                if e["type"] == "task_complete" and e["task"] == "keywords"
            ),
            None,
        )
        assert keywords_event is not None
        assert keywords_event["data"] == sample_keyword_response

        # Check last event
        assert events[-1]["type"] == "complete"
        assert events[-1]["message"] == "Analysis complete"
