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
        query="What are the main challenges of sending humans to Mars?",
        topic="Space exploration",
        level="College"
    )
    assert answer  
    assert contexts == []
    assert refs == []

def test_retrieve_answer_with_results(mock_qdrant):
    """Verify that contexts and references are extracted properly for space exploration."""
    mock_qdrant([
        {
            "text": "Sending humans to Mars involves overcoming challenges such as radiation exposure and long-duration space travel.",
            "source": "Mars Exploration",
            "chunk_index": 0,
            "source_url": "http://example.com/mars"
        }
    ])
    answer, contexts, refs = retrieval_system.retrieve_answer(
        query="What are the main challenges of sending humans to Mars?",
        topic="Space exploration",
        level="College"
    )
    assert any("radiation exposure" in c["text"] or "space travel" in c["text"] for c in contexts)
    assert any(r.get("url") == "http://example.com/mars" for r in refs)
