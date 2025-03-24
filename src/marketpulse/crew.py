from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .tools.market_tool import FinancialNewsSearchTool, StockQuoteTool, InfluencerMonitorTool
from dotenv import load_dotenv

@CrewBase
class MarketSentimentCrew:
    """Market Sentiment Analysis crew for analyzing financial markets"""

    def __init__(self):
        load_dotenv()
        self.news_tool = FinancialNewsSearchTool()
        self.stock_tool = StockQuoteTool()
        self.influencer_tool = InfluencerMonitorTool()

    @agent
    def global_news_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['global_news_agent'],
            tools=[self.news_tool],
            llm_config={"temperature": 0.3, "model": "gpt-4o-mini"},
            verbose=True
        )

    @agent
    def portfolio_news_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['portfolio_news_agent'],
            tools=[self.news_tool, self.stock_tool],
            llm_config={"temperature": 0.3, "model": "gpt-4o-mini"},
            verbose=True
        )

    @agent
    def influencer_monitor_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['influencer_monitor_agent'],
            tools=[self.influencer_tool],
            llm_config={"temperature": 0.3, "model": "gpt-4o-mini"},
            verbose=True
        )

    @agent
    def sentiment_analysis_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['sentiment_analysis_agent'],
            llm_config={"temperature": 0.0, "model": "gpt-4o-mini"},
            verbose=True
        )

    @agent
    def portfolio_strategy_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['portfolio_strategy_agent'],
            tools=[self.stock_tool],
            llm_config={"temperature": 0.2, "model": "gpt-4o-mini"},
            verbose=True
        )

    @task
    def collect_global_news_task(self) -> Task:
        return Task(
            config=self.tasks_config['collect_global_news_task']
        )

    @task
    def analyze_portfolio_news_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_portfolio_news_task']
        )

    @task
    def monitor_key_influencers_task(self) -> Task:
        return Task(
            config=self.tasks_config['monitor_key_influencers_task']
        )

    @task
    def analyze_market_sentiment_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_market_sentiment_task']
        )

    @task
    def generate_recommendations_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_recommendations_task']
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )