# tests/test_stream_utils.py

import json

import pytest

from howdoyoufindme.utils.stream_utils import create_stream_event, process_task_result


@pytest.mark.asyncio
async def test_create_stream_event_status():
    event = await create_stream_event("status", message="Processing...")
    parsed = json.loads(event.strip())
    assert parsed["type"] == "status"
    assert parsed["message"] == "Processing..."


@pytest.mark.asyncio
async def test_create_stream_event_task_complete():
    data = {"result": "test_data"}
    event = await create_stream_event("task_complete", task="test_task", data=data)
    parsed = json.loads(event.strip())
    assert parsed["type"] == "task_complete"
    assert parsed["task"] == "test_task"
    assert parsed["data"] == data


@pytest.mark.asyncio
async def test_process_task_result_success(sample_keyword_response):
    raw_result = json.dumps(sample_keyword_response)
    event = await process_task_result("keywords", raw_result)
    parsed = json.loads(event.strip())
    assert parsed["type"] == "task_complete"
    assert parsed["task"] == "keywords"
    assert parsed["data"] == sample_keyword_response


@pytest.mark.asyncio
async def test_process_task_result_invalid_json():
    invalid_json = "{invalid:json"
    event = await process_task_result("keywords", invalid_json)
    parsed = json.loads(event.strip())
    assert parsed["type"] == "error"
    assert "Failed to process keywords output" in parsed["message"]