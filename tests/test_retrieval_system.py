from sciencesage import retrieval_system

def test_embed_text_returns_vector():
    from sciencesage.retrieval_system import embed_text
    vec = embed_text("test")
    assert isinstance(vec, list)
    assert len(vec) == 1536
    assert all(v == 0.0 for v in vec)

def test_retrieve_answer_with_no_results(mock_qdrant):
    """When Qdrant returns no points, answer still comes back with safe context."""
    mock_qdrant([])  # no points
    answer, contexts, refs = retrieval_system.retrieve_answer(
        query="What is AI?", topic="AI", level="College"
    )
    assert answer  # answer is still generated
    assert contexts == []
    assert refs == []

def test_retrieve_answer_with_results(mock_qdrant):
    """Verify that contexts and references are extracted properly."""
    mock_qdrant([
        {
            "text": "AI is the study of intelligent agents.",
            "source": "test_source",
            "chunk_index": 0,
            "reference_urls": ["http://example.com/ai"]
        }
    ])
    answer, contexts, refs = retrieval_system.retrieve_answer(
        query="What is AI?", topic="AI", level="College"
    )
    assert any("AI is the study" in c for c in contexts)
    assert refs == ["http://example.com/ai"]
