# src/howdoyoufindme/utils/task_processor.py

from typing import AsyncGenerator
from crewai import Process

from ..crew import HowDoYouFindMeCrew
from .stream_utils import create_stream_event, process_task_result


async def format_sse(data: str) -> str:
    """Format string as SSE data"""
    return f"data: {data}\n\n"


async def stream_results(query: str, use_sse_format: bool = True) -> AsyncGenerator[str, None]:
    """Process tasks and stream results"""
    try:
        crew_instance = HowDoYouFindMeCrew()
        # Create crew to execute tasks
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

        # Keywords task
        event = await create_stream_event(
            event_type="status", message="Analyzing industry and competitors..."
        )
        async for msg in yield_event(event):
            yield msg
            
        keywords_task = crew_instance.generate_keywords_task()
        keywords_result = my_crew.execute_task(keywords_task, context={"query": query})
        event = await process_task_result("keywords", keywords_result.raw)
        async for msg in yield_event(event):
            yield msg

        # Query task
        event = await create_stream_event(
            event_type="status", message="Researching market position..."
        )
        async for msg in yield_event(event):
            yield msg
            
        query_task = crew_instance.build_query_task()
        query_result = my_crew.execute_task(query_task, context={"query": query})

        # Ranking task
        event = await create_stream_event(
            event_type="status", message="Analyzing competitive ranking..."
        )
        async for msg in yield_event(event):
            yield msg
            
        ranking_task = crew_instance.ranking_task()
        ranking_result = my_crew.execute_task(ranking_task, context={"query": query})
        event = await process_task_result("ranking", ranking_result.raw)
        async for msg in yield_event(event):
            yield msg

        # Complete
        event = await create_stream_event(
            event_type="complete", message="Analysis complete"
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