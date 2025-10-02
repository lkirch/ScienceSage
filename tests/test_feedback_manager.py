import json
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def temp_feedback_file(tmp_path, monkeypatch):
    feedback_file = tmp_path / "feedback.jsonl"
    # Patch FEEDBACK_FILE in feedback_manager to use the temp file
    monkeypatch.setattr("sciencesage.feedback_manager.FEEDBACK_FILE", str(feedback_file))
    return feedback_file

def test_save_feedback_creates_file_and_writes_row(temp_feedback_file, monkeypatch):
    monkeypatch.setattr("sciencesage.feedback_manager.logger", MagicMock())
    from sciencesage.feedback_manager import save_feedback # Import here to ensure monkeypatching is effective
    save_feedback("q", "a", "math", "easy", "positive")
    assert temp_feedback_file.exists()
    with open(temp_feedback_file) as f:
        lines = f.readlines()
    assert len(lines) == 1
    row = json.loads(lines[0])
    assert set(row.keys()) == {"timestamp", "query", "answer", "topic", "level", "feedback"}
    assert row["query"] == "q"
    assert row["answer"] == "a"
    assert row["topic"] == "math"
    assert row["level"] == "easy"
    assert row["feedback"] == "positive"

def test_save_feedback_appends_rows(temp_feedback_file, monkeypatch):
    monkeypatch.setattr("sciencesage.feedback_manager.logger", MagicMock())
    from sciencesage.feedback_manager import save_feedback # Import here to ensure monkeypatching is effective
    save_feedback("q1", "a1", "science", "medium", "negative")
    save_feedback("q2", "a2", "history", "hard", "positive")
    with open(temp_feedback_file) as f:
        lines = f.readlines()
    assert len(lines) == 2
    row1 = json.loads(lines[0])
    row2 = json.loads(lines[1])
    assert row1["query"] == "q1"
    assert row2["query"] == "q2"

def test_save_feedback_handles_exception(monkeypatch, tmp_path):
    # Patch logger to a mock to check error logging
    mock_logger = MagicMock()
    monkeypatch.setattr("sciencesage.feedback_manager.logger", mock_logger)
    # Patch FEEDBACK_FILE to a directory (writing as file will fail)
    feedback_file = tmp_path / "not_a_file"
    feedback_file.mkdir()
    monkeypatch.setattr("sciencesage.feedback_manager.FEEDBACK_FILE", str(feedback_file))
    from sciencesage.feedback_manager import save_feedback  # Import here after patching
    save_feedback("q", "a", "t", "l", "f")
    assert mock_logger.error.called