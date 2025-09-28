import pytest
from sciencesage.retrieval_system import retrieve_answer, rephrase_query

def test_retrieve_answer_basic():
    # These values should exist in your Qdrant collection for the test to pass
    query = "What are the main challenges of space exploration?"
    topic = "Space exploration"
    level = "College"
    answer, contexts, references = retrieve_answer(query, topic, level)
    assert isinstance(answer, str)
    assert isinstance(contexts, list)
    assert isinstance(references, list)
    assert len(contexts) > 0
    assert len(references) > 0

def test_retrieve_answer_no_results():
    query = "This is a nonsense query that should not match anything"
    topic = "Space exploration"
    level = "College"
    answer, contexts, references = retrieve_answer(query, topic, level)
    assert answer.startswith("I don’t know") or answer.startswith("Sorry")
    assert contexts == []
    assert references == []

def test_rephrase_query():
    query = "space moon landing explain"
    rephrased = rephrase_query(query)
    assert isinstance(rephrased, str)
    assert len(rephrased) > 0
    assert rephrased != query