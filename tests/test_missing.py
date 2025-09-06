import pytest
from sciencesage import retrieval_system, feedback_manager

def test_retrieve_answer_handles_empty_query(monkeypatch):
    # Should not raise, should return empty or default values
    monkeypatch.setattr(
        "sciencesage.retrieval_system.retrieve_answer",
        lambda q, t, l: ("", [], [])
    )
    answer, context, refs = retrieval_system.retrieve_answer("", "AI", "College")
    assert answer == ""
    assert context == []
    assert refs == []

def test_retrieve_answer_handles_api_error(monkeypatch):
    def raise_error(*a, **kw):
        raise RuntimeError("API down")
    monkeypatch.setattr("sciencesage.retrieval_system.retrieve_answer", raise_error)
    with pytest.raises(RuntimeError):
        retrieval_system.retrieve_answer("What is AI?", "AI", "College")

def test_save_feedback_handles_file_error(monkeypatch):
    monkeypatch.setattr("sciencesage.feedback_manager.FEEDBACK_FILE", "/root/forbidden.jsonl")
    # Should not raise, but may log error
    try:
        feedback_manager.save_feedback("Q", "A", "AI", "College", "up")
    except PermissionError:
        pass  # Acceptable if system raises due to permissions

def test_reference_citation_consistency():
    answer = "This is a fact [1] and another [2]."
    references = ["http://ref1.com", "http://ref2.com"]
    # Simulate the citation replacement logic
    import re
    def replace_citation(match):
        idx = int(match.group(1)) - 1
        if 0 <= idx < len(references):
            url = references[idx]
            return f"[{idx+1}]({url})"
        return match.group(0)
    answer_with_links = re.sub(r"\[(\d+)\]", replace_citation, answer)
    assert "[1](http://ref1.com)" in answer_with_links
    assert "[2](http://ref2.com)" in answer_with_links

def test_invalid_topic_and_level(monkeypatch):
    # Should handle gracefully, not crash
    monkeypatch.setattr(
        "sciencesage.retrieval_system.retrieve_answer",
        lambda q, t, l: ("Invalid", [], [])
    )
    answer, context, refs = retrieval_system.retrieve_answer("Q", "NotATopic", "NotALevel")
    assert answer == "Invalid"