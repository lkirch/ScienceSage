import pytest
from collections import Counter

from scripts.validate_ground_truth_dataset import validate_line, REQUIRED_FIELDS
from sciencesage.config import LEVELS

class DummyLogger:
    def __init__(self):
        self.errors = []
    def error(self, msg):
        self.errors.append(msg)

@pytest.fixture(autouse=True)
def patch_logger(monkeypatch):
    dummy = DummyLogger()
    monkeypatch.setattr("scripts.validate_ground_truth_dataset.logger", dummy)
    return dummy

def valid_obj():
    return {
        "chunk_id": "1",
        "topic": "Space",
        "text": "Some text",
        "level":  LEVELS[0], 
        "question": "What is space?",
        "answer": "The universe beyond Earth."
    }

def test_validate_line_all_valid(patch_logger):
    obj = valid_obj()
    seen = Counter()
    validate_line(obj, 0, seen)
    assert patch_logger.errors == []
    assert seen["what is space?"] == 1

@pytest.mark.parametrize("missing", REQUIRED_FIELDS)
def test_validate_line_missing_field(patch_logger, missing):
    obj = valid_obj()
    del obj[missing]
    seen = Counter()
    validate_line(obj, 1, seen)
    assert any(f"Missing field: {missing}" in e for e in patch_logger.errors)

def test_validate_line_invalid_level(patch_logger):
    obj = valid_obj()
    obj["level"] = "notalevel"
    seen = Counter()
    validate_line(obj, 2, seen)
    assert any("Invalid level: notalevel" in e for e in patch_logger.errors)

def test_validate_line_empty_question(patch_logger):
    obj = valid_obj()
    obj["question"] = ""
    seen = Counter()
    validate_line(obj, 3, seen)
    assert any("Empty question" in e for e in patch_logger.errors)

def test_validate_line_empty_answer(patch_logger):
    obj = valid_obj()
    obj["answer"] = ""
    seen = Counter()
    validate_line(obj, 4, seen)
    assert any("Empty answer" in e for e in patch_logger.errors)

def test_validate_line_duplicate_question(patch_logger):
    obj = valid_obj()
    seen = Counter()
    validate_line(obj, 0, seen)
    validate_line(obj, 1, seen)
    assert seen["what is space?"] == 2