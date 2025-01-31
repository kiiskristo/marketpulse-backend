# src/howdoyoufindme/flows/search_rank_flow.py

from crewai.flow.flow import Flow, listen, start, FlowState
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json

from ..crew import HowDoYouFindMeCrew

class SearchRankState(FlowState):
    """Tracks state for a single search rank analysis flow"""
    query: str
    keywords: Optional[Dict[str, Any]] = None
    queries: Optional[Dict[str, Any]] = None
    ranking: Optional[Dict[str, Any]] = None
    crew_result: Any = None  # Store the crew result for access by listeners

class SearchRankFlow(Flow[SearchRankState]):
    """Handles the flow of analyzing search rankings"""
    
    def __init__(self, query: str):
        # Initialize state before calling super().__init__()
        self.initial_state = SearchRankState(query=query)
        super().__init__()
        self.crew_instance = HowDoYouFindMeCrew()
        self.crew = self.crew_instance.crew()

    @start()
    async def analyze_keywords(self):
        """Start the analysis by processing keywords"""
        # Store crew result in state for access by other methods
        self.state.crew_result = self.crew.kickoff(inputs={"query": self.state.query})
        
        if (hasattr(self.state.crew_result, 'tasks_output') and 
            len(self.state.crew_result.tasks_output) > 0 and
            hasattr(self.state.crew_result.tasks_output[0], 'raw')):
            
            self.state.keywords = json.loads(self.state.crew_result.tasks_output[0].raw)
            return self.state.keywords
        return None

    @listen(analyze_keywords)
    async def process_queries(self, keyword_result):
        """Process search queries based on keywords"""
        if (hasattr(self.state.crew_result, 'tasks_output') and 
            len(self.state.crew_result.tasks_output) > 1 and
            hasattr(self.state.crew_result.tasks_output[1], 'raw')):
            
            self.state.queries = json.loads(self.state.crew_result.tasks_output[1].raw)
            return self.state.queries
        return None

    @listen(process_queries)
    async def determine_ranking(self, query_result):
        """Determine final rankings"""
        if (hasattr(self.state.crew_result, 'tasks_output') and 
            len(self.state.crew_result.tasks_output) > 2 and
            hasattr(self.state.crew_result.tasks_output[2], 'raw')):
            
            self.state.ranking = json.loads(self.state.crew_result.tasks_output[2].raw)
            return self.state.ranking
        return None

    async def stream_analysis(self):
        """Generator for streaming analysis events"""
        try:
            # Start analysis
            yield self._format_event("status", "Starting analysis...")
            
            # Keywords phase
            keywords = await self.analyze_keywords()
            if keywords:
                yield self._format_event("task_complete", task="keywords", data=keywords)
            
            # Queries phase
            yield self._format_event("status", "Analyzing queries...")
            queries = await self.process_queries(keywords)
            if queries:
                yield self._format_event("task_complete", task="queries", data=queries)
            
            # Ranking phase
            yield self._format_event("status", "Determining ranking...")
            ranking = await self.determine_ranking(queries)
            if ranking:
                yield self._format_event("task_complete", task="ranking", data=ranking)
            
            # Complete
            yield self._format_event("complete", "Analysis complete")
            
        except Exception as e:
            yield self._format_event("error", f"Error during analysis: {str(e)}")

    def _format_event(self, event_type: str, message: str = None, task: str = None, data: Dict = None) -> str:
        """Format an event for SSE streaming"""
        event = {"type": event_type}
        if message:
            event["message"] = message
        if task:
            event["task"] = task
        if data:
            event["data"] = data
        return f"data: {json.dumps(event)}\n\n"