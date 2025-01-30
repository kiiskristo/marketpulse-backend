# src/howdoyoufindme/utils/task_processor.py

from typing import AsyncGenerator

from ..crew import HowDoYouFindMeCrew
from .stream_utils import create_stream_event, process_task_result


async def stream_results(query: str) -> AsyncGenerator[str, None]:
    """Process tasks and stream results"""
    try:
        crew_instance = HowDoYouFindMeCrew()

        # Initial status
        yield await create_stream_event(
            event_type="status", message="Starting analysis..."
        )

        # Keywords task
        yield await create_stream_event(
            event_type="status", message="Analyzing industry and competitors..."
        )
        keywords_task = crew_instance.generate_keywords_task()
        keywords_result = await keywords_task.run_async({"query": query})
        yield await process_task_result("keywords", keywords_result.raw)

        # Query task
        yield await create_stream_event(
            event_type="status", message="Researching market position..."
        )
        query_task = crew_instance.build_query_task()
        query_result = await query_task.run_async({"query": query})

        # Ranking task
        yield await create_stream_event(
            event_type="status", message="Analyzing competitive ranking..."
        )
        ranking_task = crew_instance.ranking_task()
        ranking_result = await ranking_task.run_async({"query": query})
        yield await process_task_result("ranking", ranking_result.raw)

        # Complete
        yield await create_stream_event(
            event_type="complete", message="Analysis complete"
        )

    except Exception as e:
        yield await create_stream_event(event_type="error", message=str(e))
