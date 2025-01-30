# src/howdoyoufindme/utils/task_processor.py

from typing import AsyncGenerator
import asyncio

from ..crew import HowDoYouFindMeCrew
from .stream_utils import create_stream_event, process_task_result


async def format_sse(data: str) -> str:
    """Format string as SSE data"""
    return f"data: {data}\n\n"


async def stream_results(query: str, use_sse_format: bool = True) -> AsyncGenerator[str, None]:
    """Process tasks and stream results"""
    try:
        # Create crew instance
        crew_instance = HowDoYouFindMeCrew()

        # Helper to conditionally format as SSE
        async def yield_event(event_str: str):
            if use_sse_format:
                yield await format_sse(event_str)
            else:
                yield event_str

        # Initial status
        event = await create_stream_event(
            event_type="status", message="Starting analysis..."
        )
        async for msg in yield_event(event):
            yield msg
            await asyncio.sleep(0)  # Allow other tasks to run

        # Create crew
        my_crew = crew_instance.crew()

        # Status update before keywords
        event = await create_stream_event(
            event_type="status", message="Analyzing keywords..."
        )
        async for msg in yield_event(event):
            yield msg
            await asyncio.sleep(0)

        # Run keywords task
        crew_result = my_crew.kickoff(inputs={"query": query})

        # Process tasks in sequence with status updates
        if hasattr(crew_result, 'tasks_output'):
            tasks_info = {
                0: ("keywords", "keywords"),
                1: ("queries", "queries"),
                2: ("ranking", "ranking")
            }
            
            for idx, task_output in enumerate(crew_result.tasks_output):
                if idx in tasks_info:
                    task_id, task_name = tasks_info[idx]
                    
                    if hasattr(task_output, 'raw'):
                        # Send task result
                        event = await process_task_result(task_id, task_output.raw)
                        async for msg in yield_event(event):
                            yield msg
                            await asyncio.sleep(0)

                    # Send next status update (if not the last task)
                    if idx < len(tasks_info) - 1:
                        next_task = tasks_info[idx + 1][1]
                        event = await create_stream_event(
                            event_type="status",
                            message=f"Analyzing {next_task}..."
                        )
                        async for msg in yield_event(event):
                            yield msg
                            await asyncio.sleep(0)

        # Complete
        event = await create_stream_event(
            event_type="complete",
            message="Analysis complete"
        )
        async for msg in yield_event(event):
            yield msg

    except Exception as e:
        event = await create_stream_event(
            event_type="error", 
            message=f"Error during analysis: {str(e)}"
        )
        async for msg in yield_event(event):
            yield msg