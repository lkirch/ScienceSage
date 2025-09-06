from sciencesage.retrieval_system import retrieve_answer

def test_end_to_end_with_mock_qdrant(mock_qdrant):
    """Mini integration test: retrieval + GPT generation together."""
    mock_qdrant([
        {"text": "Neuroplasticity is the brain's ability to rewire itself.",
         "source": "test_doc",
         "chunk_index": 1,
         "reference_urls": []}
    ])
    answer, contexts, refs = retrieve_answer("Explain neuroplasticity", topic="Neuroplasticity", level="College")
    assert "Neuroplasticity" in answer or "rewire" in answer  # uses mocked GPT
    assert any("rewire" in c for c in contexts)
