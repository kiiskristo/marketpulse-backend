# tests/test_stream_utils.py

import pytest
import json
from unittest.mock import patch, MagicMock
from marketpulse.utils.stream_utils import (
    create_stream_event,
    process_task_result
)

@pytest.fixture
def sample_keyword_response():
    return {
        "category": "E-commerce",
        "competitors": ["Amazon", "Walmart", "Target"],
        "keywords": ["online retail", "e-commerce", "marketplace"],
    }

@pytest.mark.asyncio
async def test_create_stream_event_status():
    """Test creation of a status stream event"""
    event = await create_stream_event("status", message="Processing data")
    parsed = json.loads(event.strip())
    assert parsed["type"] == "status"
    assert parsed["message"] == "Processing data"

@pytest.mark.asyncio
async def test_create_stream_event_task_complete():
    """Test creation of a task_complete stream event"""
    event = await create_stream_event(
        event_type="task_complete", 
        task="test", 
        data={"result": "success"}
    )
    parsed = json.loads(event.strip())
    assert parsed["type"] == "task_complete"
    assert parsed["task"] == "test"
    assert parsed["data"]["result"] == "success"

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

@pytest.mark.asyncio
async def test_process_task_result_inner_exception():
    """Test handling of inner exception during JSON parsing"""
    with patch('marketpulse.utils.stream_utils.clean_and_parse_json', side_effect=Exception("Inner error")):
        event = await process_task_result("test_task", "{}")
        parsed = json.loads(event.strip())
        assert parsed["type"] == "error"
        assert "Unexpected error processing test_task output" in parsed["message"]

@pytest.mark.asyncio
async def test_process_task_result_json_extraction_failure():
    """Test handling when JSON extraction completely fails"""
    # Mock function to simulate JSON parse failure only for the input
    original_loads = json.loads
    def mock_loads(s):
        if s == "invalid json":
            raise json.JSONDecodeError("test error", "test doc", 0)
        return original_loads(s)
    
    with patch('json.loads', side_effect=mock_loads), \
         patch('marketpulse.utils.stream_utils.clean_and_parse_json',
               side_effect=ValueError("No valid JSON found")):
        event = await process_task_result("test_task", "invalid json")
        parsed = json.loads(event.strip())
        assert parsed["type"] == "error"
        assert "Failed to process test_task output" in parsed["message"]

@pytest.mark.asyncio
async def test_process_task_result_salvage_partial_json():
    """Test that we can extract partial JSON from an otherwise invalid response"""
    mixed_text = "Some text before {\"valid\": \"json\"} and text after"
    event = await process_task_result("partial", mixed_text)
    parsed = json.loads(event.strip())
    assert parsed["type"] == "task_complete"
    assert parsed["data"]["valid"] == "json"