# src/howdoyoufindme/utils/task_processor.py

from typing import AsyncGenerator

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

        # Run crew with query input
        crew_result = crew_instance.crew().kickoff(
            inputs={"query": query}
        )

        # Process each task output in sequence
        if hasattr(crew_result, 'tasks_output'):
            for task_output in crew_result.tasks_output:
                # Send status update for task
                event = await create_stream_event(
                    event_type="status",
                    message=f"Processing {task_output.summary}..."
                )
                async for msg in yield_event(event):
                    yield msg

                # Send task result
                if hasattr(task_output, 'raw'):
                    event = await process_task_result(
                        task_output.task_id, 
                        task_output.raw
                    )
                    async for msg in yield_event(event):
                        yield msg

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