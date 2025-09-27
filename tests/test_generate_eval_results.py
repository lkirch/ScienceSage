import json
import pytest
from pathlib import Path

from scripts import generate_eval_results

def test_generate_eval_for_entry_returns_expected_fields():
    """Test that generate_eval_for_entry returns expected evaluation fields."""
    entry = {
        "query": "What is Mars?",
        "expected_answer": "A planet.",
        "context_ids": ["0"],
        "difficulty_level": "middle_school",
        "metadata": {"topic": "planets"}
    }
    # This function should exist in your script
    result = generate_eval_results.generate_eval_for_entry(entry)
    assert isinstance(result, dict)
    for field in ["query", "expected_answer", "retrieved_answer", "score", "context_ids", "metadata"]:
        assert field in result

def test_main_creates_eval_results_file(monkeypatch, tmp_path):
    """Test that main() creates the eval results file with expected fields."""
    # Monkeypatch GOLDEN_DATA_FILE and EVAL_RESULTS_FILE to use tmp_path
    monkeypatch.setattr(generate_eval_results, "GOLDEN_DATA_FILE", str(tmp_path / "golden_data.jsonl"))
    monkeypatch.setattr(generate_eval_results, "EVAL_RESULTS_FILE", str(tmp_path / "eval_results.jsonl"))

    # Write a sample golden entry to GOLDEN_DATA_FILE
    golden_entry = {
        "query": "What is Mars?",
        "expected_answer": "A planet.",
        "context_ids": ["0"],
        "difficulty_level": "middle_school",
        "metadata": {"topic": "planets"}
    }
    with open(tmp_path / "golden_data.jsonl", "w", encoding="utf-8") as f:
        f.write(json.dumps(golden_entry) + "\n")

    # Run main
    generate_eval_results.main()

    # Check that EVAL_RESULTS_FILE was created and contains expected fields
    eval_file = tmp_path / "eval_results.jsonl"
    assert eval_file.exists()
    lines = eval_file.read_text().splitlines()
    assert len(lines) > 0
    entry = json.loads(lines[0])
    for field in ["query", "expected_answer", "retrieved_answer", "score", "context_ids", "metadata"]:
        assert field in entry