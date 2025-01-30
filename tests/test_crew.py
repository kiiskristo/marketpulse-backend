import pytest
from unittest.mock import patch, MagicMock
from howdoyoufindme.crew import HowDoYouFindMeCrew
from crewai import Crew


@pytest.fixture
def mock_bing_wrapper():
    with patch('langchain_community.utilities.BingSearchAPIWrapper') as mock:
        mock_instance = MagicMock()
        mock_instance.run.return_value = "Search results"
        mock.return_value = mock_instance
        yield mock_instance


def test_crew_initialization(mock_bing_wrapper):
    crew = HowDoYouFindMeCrew()
    assert crew.search_tool is not None


@pytest.mark.asyncio
async def test_keyword_agent(mock_bing_wrapper):
    crew = HowDoYouFindMeCrew()
    agent = crew.keyword_agent()
    assert "Industry Category Analyst" in str(agent)
    assert "Identify industry category" in str(agent)


@pytest.mark.asyncio
async def test_query_builder_agent(mock_bing_wrapper):
    crew = HowDoYouFindMeCrew()
    agent = crew.query_builder_agent()
    assert "Market Research Expert" in str(agent)
    assert len(agent.tools) >= 1


@pytest.mark.asyncio
async def test_ranking_agent(mock_bing_wrapper):
    crew = HowDoYouFindMeCrew()
    agent = crew.ranking_agent()
    assert "Competitive Position Analyzer" in str(agent)


@pytest.mark.asyncio
async def test_crew_tasks(mock_bing_wrapper):
    crew = HowDoYouFindMeCrew()
    
    # Test that tasks are created successfully
    keywords_task = crew.generate_keywords_task()
    assert keywords_task is not None
    assert "generate keywords" in str(keywords_task).lower()
    
    query_task = crew.build_query_task()
    assert query_task is not None
    assert "query" in str(query_task).lower()
    
    ranking_task = crew.ranking_task()
    assert ranking_task is not None
    assert "ranking" in str(ranking_task).lower()
    
    
@pytest.mark.asyncio
async def test_crew_method():
    howdy_crew = HowDoYouFindMeCrew()
    my_crew = howdy_crew.crew()  # <-- Invokes the @crew method
    assert isinstance(my_crew, Crew)
    # Optionally verify other fields:
    assert my_crew.process.name == "sequential"
    assert my_crew.verbose is True