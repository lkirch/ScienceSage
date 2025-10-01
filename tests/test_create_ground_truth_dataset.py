import os
import json
import pytest
from unittest.mock import patch, MagicMock
from scripts import create_ground_truth_dataset as create_gt
from pathlib import Path

@pytest.fixture
def mock_chunks(tmp_path):
    # Create a fake chunks file with two chunks about space exploration
    chunks = [
        {
            "uuid": "chunk1",
            "topic": "Space Exploration",
            "text": "The Apollo 11 mission was the first to land humans on the Moon in 1969.",
        },
        {
            "uuid": "chunk2",
            "topic": "Space Exploration",
            "text": "The Mars Rover Perseverance landed on Mars in 2021 to search for signs of ancient life.",
        },
    ]
    chunks_file = tmp_path / "chunks.jsonl"
    with open(chunks_file, "w") as f:
        for c in chunks:
            f.write(json.dumps(c) + "\n")
    return chunks_file, chunks

@pytest.fixture(autouse=True)
def patch_config(monkeypatch, tmp_path, mock_chunks):
    # Patch config constants to use temp files and space exploration topic
    monkeypatch.setattr(create_gt, "CHUNKS_FILE", str(mock_chunks[0]))
    monkeypatch.setattr(create_gt, "GROUND_TRUTH_FILE", str(tmp_path / "ground_truth.jsonl"))
    monkeypatch.setattr(create_gt, "TOPICS", ["Space Exploration"])
    monkeypatch.setattr(create_gt, "LEVELS", ["Middle School", "College", "Advanced"])
    monkeypatch.setattr(create_gt, "EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    monkeypatch.setattr(create_gt, "CHAT_MODEL", "gpt-3.5-turbo")
    monkeypatch.setattr(create_gt, "MAX_TOKENS", 256)

def fake_generate_questions_by_level(chunk):
    # Always return a QA for each level about space exploration
    if "Apollo 11" in chunk:
        return {
            "Middle School": {
                "query": "What was the first mission to land humans on the Moon?",
                "expected_answer": "Apollo 11 was the first mission to land humans on the Moon in 1969.",
                "difficulty_level": "Middle School"
            },
            "College": {
                "query": "In what year did Apollo 11 land on the Moon?",
                "expected_answer": "1969",
                "difficulty_level": "College"
            },
            "Advanced": {
                "query": "Describe the significance of the Apollo 11 mission.",
                "expected_answer": "Apollo 11 was the first mission to land humans on the Moon, marking a major achievement in space exploration in 1969.",
                "difficulty_level": "Advanced"
            },
        }
    else:
        return {
            "Middle School": {
                "query": "What is the name of the Mars rover that landed in 2021?",
                "expected_answer": "Perseverance",
                "difficulty_level": "Middle School"
            },
            "College": {
                "query": "What was the main goal of the Perseverance rover mission?",
                "expected_answer": "To search for signs of ancient life on Mars.",
                "difficulty_level": "College"
            },
            "Advanced": {
                "query": "Explain the scientific objectives of the Perseverance rover on Mars.",
                "expected_answer": "The Perseverance rover landed on Mars in 2021 to search for signs of ancient life and collect samples for future return to Earth.",
                "difficulty_level": "Advanced"
            },
        }

def test_main_creates_ground_truth(monkeypatch, tmp_path):
    # Patch out model loading and OpenAI calls
    monkeypatch.setattr(create_gt, "SentenceTransformer", lambda model: None)
    monkeypatch.setattr(create_gt, "generate_questions_by_level", fake_generate_questions_by_level)

    create_gt.main()

    # Check that the ground truth file was created and has content
    gt_path = Path(create_gt.GROUND_TRUTH_FILE)
    assert gt_path.exists()
    lines = list(gt_path.open())
    assert len(lines) > 0
    for line in lines:
        obj = json.loads(line)
        assert "chunk_id" in obj
        assert "topic" in obj
        assert obj["topic"] == "Space Exploration"
        assert "text" in obj
        assert "level" in obj
        assert "question" in obj
        assert "answer" in obj