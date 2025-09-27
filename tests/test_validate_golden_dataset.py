import json
import pytest
from pathlib import Path

from scripts import create_golden_dataset

def test_generate_questions_returns_list():
    """Test that generate_questions returns a list of Q&A dicts."""
    sample_text = "Mars is the fourth planet from the Sun."
    qas = create_golden_dataset.generate_questions(sample_text)
    assert isinstance(qas, list)
    assert all(isinstance(qa, dict) for qa in qas)
    assert all("query" in qa and "expected_answer" in qa for qa in qas)

def test_main_creates_golden_data_file(monkeypatch, tmp_path):
    """Test that main() creates the golden data file with expected fields."""
    # Monkeypatch CHUNKS_FILE and GOLDEN_DATA_FILE to use tmp_path
    monkeypatch.setattr(create_golden_dataset, "CHUNKS_FILE", str(tmp_path / "chunks.jsonl"))
    monkeypatch.setattr(create_golden_dataset, "GOLDEN_DATA_FILE", str(tmp_path / "golden_data.jsonl"))

    # Write a sample chunk to CHUNKS_FILE
    chunk = {
        "id": "0",
        "text": "Mars is the fourth planet from the Sun.",
        "topic": "planets"
    }
    with open(tmp_path / "chunks.jsonl", "w", encoding="utf-8") as f:
        f.write(json.dumps(chunk) + "\n")

    # Run main
    create_golden_dataset.main()

    # Check that GOLDEN_DATA_FILE was created and contains expected fields
    golden_file = tmp_path / "golden_data.jsonl"
    assert golden_file.exists()
    lines = golden_file.read_text().splitlines()
    assert len(lines) > 0
    entry = json.loads(lines[0])
    for field in ["query", "expected_answer", "context_ids", "difficulty_level", "metadata"]:
        assert field in entry
    assert entry["context_ids"] == ["0"]
    assert entry["metadata"]["topic"] == "planets"