# tests/test_api.py

def test_health_check(test_client):
    """Test the health check endpoint"""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_search_rank_flow_endpoint_setup(test_client):
    """Test the search rank flow endpoint returns proper SSE setup"""
    response = test_client.get("/api/search-rank/flow?query=test_company")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream"
    assert response.headers["cache-control"] == "no-cache"
    assert response.headers["connection"] == "keep-alive"


def test_search_rank_flow_missing_query(test_client):
    """Test handling of missing query parameter"""
    response = test_client.get("/api/search-rank/flow")
    assert response.status_code == 422  # FastAPI's validation error status code