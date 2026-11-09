"""API contract checks without downloading models or reading private files."""
from fastapi.testclient import TestClient
from backend.app import app, ask, Question


def test_public_aggregates_and_health():
    client = TestClient(app)
    health = client.get('/health')
    assert health.status_code == 503 and health.json()['demo_only'] is True
    analytics = client.get('/analytics')
    assert analytics.status_code == 200
    assert analytics.json()['rows'] == 377719
    assert 'records' not in analytics.json()


def test_query_validation():
    client = TestClient(app)
    assert client.post('/ask', json={'question': ''}).status_code == 422
    assert client.post('/ask', json={'question': 'x' * 301}).status_code == 422


def test_health_exposes_readiness_state():
    client = TestClient(app)
    app.state.models_ready = False
    app.state.index_ready = False
    app.state.startup_error = "TestError"
    response = client.get('/health')
    assert response.status_code == 503
    assert response.json() == {
        "status": "starting", "demo_only": True,
        "models_ready": False, "index_ready": False,
        "model_mode": "starting", "rss_mb": response.json()["rss_mb"],
        "startup_error": "TestError",
    }


def test_lifespan_initializer_is_deferred():
    import inspect
    from backend.app import initialize_rag
    assert inspect.isfunction(initialize_rag)


def test_ask_contract_with_mocked_ready_rag():
    class FakeEmbedder:
        def encode(self, *_args, **_kwargs):
            import numpy as np
            return np.array([[1.0, 0.0]])
    class FakeCollection:
        def count(self): return 1
        def query(self, **_kwargs):
            return {"documents": [["A verified demo snippet."]], "metadatas": [[{"file": "demo.pdf", "page": 1}]], "distances": [[0.1]]}
    app.state.models_ready = True
    app.state.index_ready = True
    app.state.rag = (FakeCollection(), FakeEmbedder(), lambda _prompt: "A cited demo answer")
    response = ask(Question(question="What does the demo say?"))
    assert response["answer"] == "A cited demo answer"
    assert response["sources"][0]["page"] == 1


def test_lightweight_embedder_is_deterministic():
    from backend.app import HashEmbedder
    embedder = HashEmbedder()
    assert embedder.encode(["draft pressure"])[0] == embedder.encode(["draft pressure"])[0]
