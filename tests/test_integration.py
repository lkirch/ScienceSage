from sciencesage.retrieval_system import retrieve_answer

def test_end_to_end_with_mock_qdrant(mock_qdrant):
    """Mini integration test: retrieval + GPT generation together for space exploration topics."""
    mock_qdrant([
        {
            "text": "Sending humans to Mars involves overcoming challenges such as radiation exposure and long-duration space travel.",
            "source": "Mars Exploration",
            "chunk_index": 0,
            "reference_urls": []
        }
    ])
    answer, contexts, refs = retrieve_answer(
        "What are the main challenges of sending humans to Mars?",
        topic="Space exploration",
        level="College"
    )
    assert "Mars" in answer or "radiation" in answer or "space travel" in answer
    assert any("radiation" in c["text"] or "space travel" in c["text"] for c in contexts)
