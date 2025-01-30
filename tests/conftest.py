from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from howdoyoufindme.crew import HowDoYouFindMeCrew
from howdoyoufindme.main import app


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def mock_crew():
    crew = MagicMock(spec=HowDoYouFindMeCrew)
    # Mock the task methods to return AsyncMock instances
    crew.generate_keywords_task.return_value = AsyncMock()
    crew.build_query_task.return_value = AsyncMock()
    crew.ranking_task.return_value = AsyncMock()
    return crew


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
