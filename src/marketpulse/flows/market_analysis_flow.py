# src/market_sentiment/flows/sentiment_analysis_flow.py

from crewai.flow.flow import Flow, listen, start, FlowState
from crewai import Agent, Crew, Process
from pydantic import BaseModel
from typing import Dict, Any, Optional, AsyncGenerator, List
import json
import asyncio
import logging
import re
from ..clean_json import clean_and_parse_json
from ..crew import MarketSentimentCrew

class MarketSentimentState(FlowState):
    portfolio: Dict[str, Any]
    preferences: Dict[str, Any]
    global_news: Optional[Dict[str, Any]] = None
    portfolio_news: Optional[Dict[str, Any]] = None
    influencer_data: Optional[Dict[str, Any]] = None
    sentiment_analysis: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, Any]] = None

class MarketSentimentFlow(Flow[MarketSentimentState]):
    def __init__(self, portfolio: Dict[str, Any], preferences: Dict[str, Any]):
        self.initial_state = MarketSentimentState(
            portfolio=portfolio,
            preferences=preferences
        )
        super().__init__()
        self._initialize_crew()

    def _initialize_crew(self):
        """Initialize crew instance with separate crews for each task"""
        self.crew_instance = MarketSentimentCrew()
        
        self.global_news_crew = Crew(
            agents=[self.crew_instance.global_news_agent()],
            tasks=[self.crew_instance.collect_global_news_task()],
            process=Process.sequential,
            verbose=True
        )
        
        self.portfolio_news_crew = Crew(
            agents=[self.crew_instance.portfolio_news_agent()],
            tasks=[self.crew_instance.analyze_portfolio_news_task()],
            process=Process.sequential,
            verbose=True
        )
        
        self.influencer_crew = Crew(
            agents=[self.crew_instance.influencer_monitor_agent()],
            tasks=[self.crew_instance.monitor_key_influencers_task()],
            process=Process.sequential,
            verbose=True
        )
        
        self.sentiment_crew = Crew(
            agents=[self.crew_instance.sentiment_analysis_agent()],
            tasks=[self.crew_instance.analyze_market_sentiment_task()],
            process=Process.sequential,
            verbose=True
        )
        
        self.recommendation_crew = Crew(
            agents=[self.crew_instance.portfolio_strategy_agent()],
            tasks=[self.crew_instance.generate_recommendations_task()],
            process=Process.sequential,
            verbose=True
        )

    def _extract_json_from_response(self, text: str) -> Optional[Dict]:
        """Extract and clean JSON from agent response"""
        try:
            # First try direct JSON parsing
            return json.loads(text)
        except json.JSONDecodeError:
            try:
                # Find content between first { and last }
                start_idx = text.find('{')
                end_idx = text.rfind('}')
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = text[start_idx:end_idx + 1]
                    # Remove escaped quotes that might be causing issues
                    json_str = re.sub(r'\\+"', '"', json_str)
                    return json.loads(json_str)
            except Exception:
                try:
                    # Last resort: try clean_and_parse_json
                    return clean_and_parse_json(text)
                except Exception as e:
                    logging.error(f"Failed to parse JSON: {str(e)}\nRaw text: {text[:200]}...")
                    return None

    def _get_key_influencers(self) -> List[str]:
        """Get list of key influencers to monitor based on market relevance"""
        return [
            "Jerome Powell",
            "Janet Yellen",
            "Elon Musk",
            "Warren Buffett",
            "Jamie Dimon"
        ]

    def _format_portfolio_for_task(self) -> str:
        """Format portfolio data for task input"""
        portfolio_str = json.dumps(self.state.portfolio)
        return portfolio_str
        
    def _format_preferences_for_task(self) -> str:
        """Format preferences data for task input"""
        preferences_str = json.dumps(self.state.preferences)
        return preferences_str

    @start()
    async def collect_global_news(self):
        """Start the analysis by collecting global financial news"""
        try:
            result = self.global_news_crew.kickoff(inputs={})
            if hasattr(result.tasks_output[0], 'raw'):
                data = self._extract_json_from_response(result.tasks_output[0].raw)
                if data:
                    self.state.global_news = data
                    return data
        except Exception as e:
            logging.error(f"Error in collect_global_news: {str(e)}")
        return None

    @listen(collect_global_news)
    async def analyze_portfolio_news(self, global_news_result):
        """Analyze news specific to the user's portfolio"""
        try:
            result = self.portfolio_news_crew.kickoff(inputs={
                "portfolio": self._format_portfolio_for_task()
            })
            if hasattr(result.tasks_output[0], 'raw'):
                data = self._extract_json_from_response(result.tasks_output[0].raw)
                if data:
                    self.state.portfolio_news = data
                    return data
        except Exception as e:
            logging.error(f"Error in analyze_portfolio_news: {str(e)}")
        return None

    @listen(analyze_portfolio_news)
    async def monitor_key_influencers(self, portfolio_news_result):
        """Monitor statements from key market influencers"""
        try:
            # Get a list of influencers to monitor
            influencers = self._get_key_influencers()
            
            # Execute the task
            result = self.influencer_crew.kickoff(inputs={})
            
            if hasattr(result.tasks_output[0], 'raw'):
                data = self._extract_json_from_response(result.tasks_output[0].raw)
                if data:
                    self.state.influencer_data = data
                    return data
        except Exception as e:
            logging.error(f"Error in monitor_key_influencers: {str(e)}")
        return None

    @listen(monitor_key_influencers)
    async def analyze_market_sentiment(self, influencer_result):
        """Analyze overall market sentiment based on all collected data"""
        try:
            result = self.sentiment_crew.kickoff(inputs={})
            
            if hasattr(result.tasks_output[0], 'raw'):
                data = self._extract_json_from_response(result.tasks_output[0].raw)
                if data:
                    self.state.sentiment_analysis = data
                    return data
        except Exception as e:
            logging.error(f"Error in analyze_market_sentiment: {str(e)}")
        return None

    @listen(analyze_market_sentiment)
    async def generate_recommendations(self, sentiment_result):
        """Generate portfolio recommendations based on sentiment analysis"""
        try:
            result = self.recommendation_crew.kickoff(inputs={
                "portfolio": self._format_portfolio_for_task(),
                "preferences": self._format_preferences_for_task()
            })
            
            if hasattr(result.tasks_output[0], 'raw'):
                data = self._extract_json_from_response(result.tasks_output[0].raw)
                if data:
                    self.state.recommendations = data
                    return data
        except Exception as e:
            logging.error(f"Error in generate_recommendations: {str(e)}")
        return None

    async def stream_analysis(self) -> AsyncGenerator[str, None]:
        """Stream the analysis process"""
        try:
            yield self._format_event("status", "Starting market sentiment analysis...")
            await asyncio.sleep(0.1)

            global_news = await self.collect_global_news()
            if global_news:
                yield self._format_event("task_complete", task="global_news", data=global_news)
                yield self._format_event("status", "Analyzing portfolio-specific news...")
                
                portfolio_news = await self.analyze_portfolio_news(global_news)
                if portfolio_news:
                    yield self._format_event("task_complete", task="portfolio_news", data=portfolio_news)
                    yield self._format_event("status", "Monitoring key market influencers...")
                    
                    influencer_data = await self.monitor_key_influencers(portfolio_news)
                    if influencer_data:
                        yield self._format_event("task_complete", task="influencer_data", data=influencer_data)
                        yield self._format_event("status", "Analyzing market sentiment...")
                        
                        sentiment_analysis = await self.analyze_market_sentiment(influencer_data)
                        if sentiment_analysis:
                            yield self._format_event("task_complete", task="sentiment_analysis", data=sentiment_analysis)
                            yield self._format_event("status", "Generating trading recommendations...")
                            
                            recommendations = await self.generate_recommendations(sentiment_analysis)
                            if recommendations:
                                yield self._format_event("task_complete", task="recommendations", data=recommendations)
                                yield self._format_event("complete", "Market sentiment analysis complete")
                            else:
                                yield self._format_event("error", "Failed to generate recommendations")
                        else:
                            yield self._format_event("error", "Failed to analyze market sentiment")
                    else:
                        yield self._format_event("error", "Failed to monitor key influencers")
                else:
                    yield self._format_event("error", "Failed to analyze portfolio news")
            else:
                yield self._format_event("error", "Failed to collect global news")
                    
        except Exception as e:
            logging.error(f"Error in stream_analysis: {str(e)}")
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