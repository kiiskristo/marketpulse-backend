# tests/test_crew.py

import pytest
from unittest.mock import patch, MagicMock
from crewai import Crew
from howdoyoufindme.crew import HowDoYouFindMeCrew


def test_crew_initialization(mock_bing_wrapper):
    crew = HowDoYouFindMeCrew()
    assert crew.search_tool is not None


def test_keyword_agent(mock_bing_wrapper):
    crew = HowDoYouFindMeCrew()
    agent = crew.keyword_agent()
    assert "Industry Category Analyst" == agent.role


def test_query_builder_agent(mock_bing_wrapper):
    crew = HowDoYouFindMeCrew()
    agent = crew.query_builder_agent()
    assert "Market Research Expert" == agent.role
    assert len(agent.tools) >= 1


def test_ranking_agent(mock_bing_wrapper):
    crew = HowDoYouFindMeCrew()
    agent = crew.ranking_agent()
    assert "Competitive Position Analyzer" == agent.role


def test_crew_tasks(mock_bing_wrapper):
    crew = HowDoYouFindMeCrew()
    
    keywords_task = crew.generate_keywords_task()
    assert keywords_task is not None
    assert "Test description" == keywords_task.description
    
    query_task = crew.build_query_task()
    assert query_task is not None
    assert "Test description" == query_task.description
    
    ranking_task = crew.ranking_task()
    assert ranking_task is not None
    assert "Test description" == ranking_task.description


def test_crew_method(mock_bing_wrapper):
    crew_instance = HowDoYouFindMeCrew()
    my_crew = crew_instance.crew()
    assert isinstance(my_crew, Crew)
    assert my_crew.process.name == "sequential"
    assert my_crew.verbose is True