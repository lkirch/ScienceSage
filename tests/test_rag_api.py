from fastapi.testclient import TestClient
import pytest

from sciencesage.rag_api import app

@pytest.fixture
def client():
    return TestClient(app)

def test_rag_endpoint_success(monkeypatch, client):
    # Mock retrieve_answer to return a predictable result
    def mock_retrieve_answer(query, topic, level, top_k):
        return {
            "answer": "Mocked answer.",
            "context_chunks": ["chunk1", "chunk2"],
            "sources": ["source1", "source2"]
        }
    import sciencesage.rag_api
    monkeypatch.setattr(sciencesage.rag_api, "retrieve_answer", mock_retrieve_answer)

    payload = {
        "query": "What is the moon?",
        "topic": "Space Exploration",
        "level": "middle_school",
        "top_k": 2
    }
    response = client.post("/rag", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Mocked answer."
    assert data["context_chunks"] == ["chunk1", "chunk2"]
    assert data["sources"] == ["source1", "source2"]

def test_rag_endpoint_error(monkeypatch, client):
    # Mock retrieve_answer to raise an exception
    def mock_retrieve_answer(query, topic, level, top_k):
        raise RuntimeError("Test error")
    import sciencesage.rag_api
    monkeypatch.setattr(sciencesage.rag_api, "retrieve_answer", mock_retrieve_answer)

    payload = {
        "query": "What is the moon?",
        "topic": "Space Exploration",
        "level": "middle_school",
        "top_k": 2
    }
    response = client.post("/rag", json=payload)
    assert response.status_code == 500
    assert response.json()["detail"] == "Test error"