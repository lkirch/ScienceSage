import pytest
from sciencesage.retrieval_system import retrieve_context, generate_answer, retrieve_answer

def test_retrieve_context_returns_chunks():
    query = "What is photosynthesis?"
    chunks = retrieve_context(query, top_k=3, level="College")
    assert isinstance(chunks, list)
    # If your Qdrant DB is empty, this may be 0; otherwise, should be >0
    for chunk in chunks:
        assert "text" in chunk
        assert "source_url" in chunk
        assert "chunk_id" in chunk
        assert "score" in chunk

def test_generate_answer_returns_string():
    query = "Explain gravity."
    # Simulate context chunks
    context_chunks = [
        {"text": "Gravity is a force...", "source_url": "Physics Book", "chunk_id": 1, "score": 0.95},
        {"text": "It attracts objects...", "source_url": "Science Journal", "chunk_id": 2, "score": 0.93},
    ]
    answer = generate_answer(query, context_chunks, level="College", topic="Physics")
    assert isinstance(answer, str)
    assert len(answer) > 0

def test_retrieve_answer_fallback():
    # Use a nonsense query to trigger fallback
    query = "asdkjashdkjahsdkjahsd"
    answer = retrieve_answer(query, topic="Unknown", level="College", top_k=2)
    assert isinstance(answer, str)
    assert "I don’t know" in answer or "Sorry" in answer

def test_retrieve_answer_success():
    # This test assumes your Qdrant DB has relevant data for the topic
    query = "Describe the process of cell division."
    answer = retrieve_answer(query, topic="Biology", level="College", top_k=2)
    assert isinstance(answer, str)
    assert len(answer) > 0