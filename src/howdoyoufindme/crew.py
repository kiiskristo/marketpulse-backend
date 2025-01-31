from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .tools.search_tool import MarketSearchTool
from dotenv import load_dotenv

@CrewBase
class HowDoYouFindMeCrew:
    """HowDoYouFindMe crew for analyzing online presence"""

    def __init__(self):
        load_dotenv()
        self.search_tool = MarketSearchTool()

    @agent
    def keyword_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['keyword_agent'],
            llm_config={"temperature": 0.7, "model": "gpt-4o-mini"},
            verbose=True
        )

    @agent
    def query_builder_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['query_builder_agent'],
            tools=[self.search_tool],
            llm_config={"temperature": 0.7, "model": "gpt-4o-mini"},
            verbose=True
        )

    @agent
    def ranking_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['ranking_agent'],
            llm_config={"temperature": 0.0, "model": "gpt-4o-mini"},
            verbose=True
        )

    @task
    def generate_keywords_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_keywords_task']
        )

    @task
    def build_query_task(self) -> Task:
        return Task(
            config=self.tasks_config['build_query_task']
        )

    @task
    def ranking_task(self) -> Task:
        return Task(
            config=self.tasks_config['ranking_task']
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )