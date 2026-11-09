"""API contract checks without downloading models or reading private files."""
from fastapi.testclient import TestClient
from backend.app import app


def test_public_aggregates_and_health():
    client = TestClient(app)
    health = client.get('/health')
    assert health.status_code == 200 and health.json()['demo_only'] is True
    analytics = client.get('/analytics')
    assert analytics.status_code == 200
    assert analytics.json()['rows'] == 377719
    assert 'records' not in analytics.json()


def test_query_validation():
    client = TestClient(app)
    assert client.post('/ask', json={'question': ''}).status_code == 422
    assert client.post('/ask', json={'question': 'x' * 301}).status_code == 422
