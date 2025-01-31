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
        my_crew = crew_instance.crew()

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
            await asyncio.sleep(0.1)  # Small delay for streaming

        # Create and run crew
        event = await create_stream_event(
            event_type="status", message="Analyzing keywords..."
        )
        async for msg in yield_event(event):
            yield msg
            await asyncio.sleep(0.1)

        # Run the crew tasks
        crew_result = my_crew.kickoff(inputs={"query": query})

        # Process results
        if hasattr(crew_result, 'tasks_output'):
            for idx, task_output in enumerate(crew_result.tasks_output):
                if idx == 0:
                    if hasattr(task_output, 'raw'):
                        event = await process_task_result("keywords", task_output.raw)
                        async for msg in yield_event(event):
                            yield msg
                            await asyncio.sleep(0.1)

                    event = await create_stream_event(
                        event_type="status",
                        message="Building search queries..."
                    )
                    async for msg in yield_event(event):
                        yield msg
                        await asyncio.sleep(0.1)

                elif idx == 1:
                    if hasattr(task_output, 'raw'):
                        event = await process_task_result("queries", task_output.raw)
                        async for msg in yield_event(event):
                            yield msg
                            await asyncio.sleep(0.1)

                    event = await create_stream_event(
                        event_type="status",
                        message="Analyzing competitive position..."
                    )
                    async for msg in yield_event(event):
                        yield msg
                        await asyncio.sleep(0.1)

                elif idx == 2:
                    if hasattr(task_output, 'raw'):
                        event = await process_task_result("ranking", task_output.raw)
                        async for msg in yield_event(event):
                            yield msg
                            await asyncio.sleep(0.1)

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