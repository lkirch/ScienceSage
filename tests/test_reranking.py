import numpy as np
import pytest
from types import SimpleNamespace

from sciencesage.retrieval_system import rerank_results, TOPIC_EMBEDDINGS

# -------------------------
# Helpers for Mocking
# -------------------------
class MockPoint:
    def __init__(self, point_id, score, topics, text="mock text"):
        self.id = point_id
        self.score = score
        self.payload = {
            "topics": topics,
            "text": text,
            "source": "test_source",
            "chunk_index": 1
        }

class MockResults:
    def __init__(self, points):
        self.points = points


@pytest.fixture
def mock_results():
    """Return mock Qdrant results with different vector scores & topics."""
    return MockResults([
        MockPoint("a", score=0.90, topics=["AI"]),       # High vector score, correct topic
        MockPoint("b", score=0.80, topics=["Neuroplasticity"]), # Lower vector score, unrelated topic
        MockPoint("c", score=0.60, topics=["AI"]),       # Low vector score, but right topic
    ])


@pytest.fixture
def mock_query_vector():
    """Use the embedding of 'AI' topic as a stand-in for query vector."""
    return np.array(TOPIC_EMBEDDINGS["AI"]).tolist()


def test_reranking_sorts_by_combined_score(mock_results, mock_query_vector):
    reranked = rerank_results(mock_results, mock_query_vector)

    # Ensure we still have 3 points
    assert len(reranked) == 3

    # Check that points are sorted in descending order of combined score
    combined_scores = []
    for p in reranked:
        topic_vecs = [TOPIC_EMBEDDINGS[t] for t in p.payload["topics"] if t in TOPIC_EMBEDDINGS]
        topic_score = 0
        if topic_vecs:
            # manually compute topic similarity to validate order
            topic_score = float(np.dot(mock_query_vector, topic_vecs[0]) /
                                (np.linalg.norm(mock_query_vector) * np.linalg.norm(topic_vecs[0])))
        combined_scores.append(0.8 * p.score + 0.2 * topic_score)

    assert combined_scores == sorted(combined_scores, reverse=True), "Reranked results not sorted correctly"


def test_reranking_boosts_correct_topics(mock_results, mock_query_vector):
    """Verify that a lower vector score can outrank a higher score if topic is more relevant."""
    reranked = rerank_results(mock_results, mock_query_vector)

    # "a" and "c" share the same topic; "c" has lower vector score but should be boosted.
    a_index = next(i for i, p in enumerate(reranked) if p.id == "a")
    c_index = next(i for i, p in enumerate(reranked) if p.id == "c")

    # c_index should still be ranked below a (since a had both high vector score + topic match)
    # but it should beat "b" which has unrelated topic
    b_index = next(i for i, p in enumerate(reranked) if p.id == "b")

    assert c_index > a_index, "Point C should still rank below A (A has stronger vector match)"
    assert c_index < b_index, "Point C should outrank B because of topic relevance boost"

