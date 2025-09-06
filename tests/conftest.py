import pytest
from unittest.mock import patch, MagicMock
from qdrant_client.models import ScoredPoint
import numpy as np

@pytest.fixture(autouse=True)
def mock_openai_embeddings(monkeypatch):
    """Auto-mock OpenAI embeddings.create for all tests."""
    fake_response = MagicMock()
    # Return a vector of the correct dimension (1536)
    fake_response.data = [MagicMock(embedding=np.zeros(1536).tolist())]
    with patch("sciencesage.retrieval_system.client.embeddings.create", return_value=fake_response):
        yield

@pytest.fixture(autouse=True)
def mock_openai_chat(monkeypatch):
    """Auto-mock OpenAI chat.completions.create for all tests."""
    fake_choice = MagicMock()
    fake_choice.message.content = "Neuroplasticity is the brain's ability to rewire itself."
    fake_completion = MagicMock()
    fake_completion.choices = [fake_choice]
    with patch("sciencesage.retrieval_system.client.chat.completions.create", return_value=fake_completion):
        yield

@pytest.fixture
def mock_qdrant(monkeypatch):
    """Fixture to mock qdrant.query_points and allow test control."""
    points = []

    def _set_points(payloads):
        nonlocal points
        points = [
            ScoredPoint(
                id=str(i),
                payload=p,
                score=0.99,
                vector=None,
                version=1
            ) for i, p in enumerate(payloads)
        ]

    def fake_query_points(*args, **kwargs):
        return MagicMock(points=points)

    monkeypatch.setattr("sciencesage.retrieval_system.qdrant.query_points", fake_query_points)
    return _set_points
