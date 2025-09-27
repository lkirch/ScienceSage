import json
import pytest
from pathlib import Path

from scripts import rag_llm_evaluation

def test_evaluate_entry_returns_expected_fields():
    """Test that evaluate_entry returns expected evaluation fields."""
    entry = {
        "query": "What is Mars?",
        "expected_answer": "A planet.",
        "retrieved_answer": "Mars is a planet.",
        "context_ids": ["0"],
        "difficulty_level": "middle_school",
        "metadata": {"topic": "planets"}
    }
    # This function should exist in your script
    result = rag_llm_evaluation.evaluate_entry(entry)
    assert isinstance(result, dict)
    for field in ["query", "expected_answer", "retrieved_answer", "llm_score", "context_ids", "metadata"]:
        assert field in result

def test_main_creates_llm_eval_file(monkeypatch, tmp_path):
    """Test that main() creates the LLM evaluation file with expected fields."""
    # Monkeypatch EVAL_RESULTS_FILE and LLM_EVAL_FILE to use tmp_path
    monkeypatch.setattr(rag_llm_evaluation, "EVAL_RESULTS_FILE", str(tmp_path / "eval_results.jsonl"))
    monkeypatch.setattr(rag_llm_evaluation, "LLM_EVAL_FILE", str(tmp_path / "llm_eval.jsonl"))

    # Write a sample eval result to EVAL_RESULTS_FILE
    eval_entry = {
        "query": "What is Mars?",
        "expected_answer": "A planet.",
        "retrieved_answer": "Mars is a planet.",
        "context_ids": ["0"],
        "difficulty_level": "middle_school",
        "metadata": {"topic": "planets"}
    }
    with open(tmp_path / "eval_results.jsonl", "w", encoding="utf-8") as f:
        f.write(json.dumps(eval_entry) + "\n")

    # Run main
    rag_llm_evaluation.main()

    # Check that LLM_EVAL_FILE was created and contains expected fields
    llm_eval_file = tmp_path / "llm_eval.jsonl"
    assert llm_eval_file.exists()
    lines = llm_eval_file.read_text().splitlines()
    assert len(lines) > 0
    entry = json.loads(lines[0])
    for field in ["query", "expected_answer", "retrieved_answer", "llm_score", "context_ids", "metadata"]:
        assert field in entry