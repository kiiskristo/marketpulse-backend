# src/howdoyoufindme/utils/stream_utils.py

import json
from typing import AsyncGenerator, Any, Dict
from ..clean_json import clean_and_parse_json


async def create_stream_event(
    event_type: str, message: str = None, task: str = None, data: Dict[str, Any] = None
) -> str:
    """Create a formatted stream event"""
    event = {"type": event_type}
    if message is not None:
        event["message"] = message
    if task is not None:
        event["task"] = task
    if data is not None:
        event["data"] = data
    return json.dumps(event) + "\n"


async def process_task_result(task_name: str, raw_result: str) -> str:
    """Process a task result and create a task_complete event"""
    try:
        parsed_data = clean_and_parse_json(raw_result)
        return await create_stream_event(
            event_type="task_complete", task=task_name, data=parsed_data
        )
    except Exception as e:
        return await create_stream_event(
            event_type="error", message=f"Error processing {task_name} result: {str(e)}"
        )
