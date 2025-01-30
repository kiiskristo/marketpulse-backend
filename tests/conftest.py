# tests/conftest.py

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from howdoyoufindme.main import app


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def mock_bing_wrapper():
    with patch('langchain_community.utilities.BingSearchAPIWrapper') as mock:
        mock_instance = MagicMock()
        mock_instance.run.return_value = "Search results"
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_keyword_response():
    return {
        "category": "E-commerce",
        "competitors": ["Amazon", "Walmart", "Target"],
        "keywords": ["online retail", "e-commerce", "marketplace"],
    }


@pytest.fixture
def sample_ranking_response():
    return {
        "ranking_position": "#3 in online retail",
        "market_context": {"market_size": "500B USD", "growth_projections": "15% YoY"},
        "comparison_to_leaders": {
            "top_competitors": [
                {"company": "Amazon", "rank": 1, "market_share": "40%"},
                {"company": "Walmart", "rank": 2, "market_share": "20%"},
            ],
            "summary": "Strong challenger in the e-commerce space",
        },
    }


@pytest.fixture(autouse=True)
def mock_config_files():
    agents_config = {
        'keyword_agent': {
            'role': 'Industry Category Analyst',
            'goal': 'Identify industry category',
            'backstory': 'Test backstory'
        },
        'query_builder_agent': {
            'role': 'Market Research Expert',
            'goal': 'Research top companies',
            'backstory': 'Test backstory'
        },
        'ranking_agent': {
            'role': 'Competitive Position Analyzer',
            'goal': 'Determine rankings',
            'backstory': 'Test backstory'
        }
    }

    tasks_config = {
        'generate_keywords_task': {
            'description': 'Test description',
            'expected_output': '{"test": "output"}',
            'agent': 'keyword_agent'
        },
        'build_query_task': {
            'description': 'Test description',
            'expected_output': '{"test": "output"}',
            'agent': 'query_builder_agent'
        },
        'ranking_task': {
            'description': 'Test description',
            'expected_output': '{"test": "output"}',
            'agent': 'ranking_agent'
        }
    }

    with patch('crewai.project.crew_base.yaml.safe_load') as mock_yaml:
        mock_yaml.side_effect = [agents_config, tasks_config]
        yield mock_yaml