import os
from pathlib import Path
from loguru import logger
import pytest
from unittest.mock import patch, MagicMock
from sciencesage import prompts, feedback_manager, retrieval_system
from sciencesage.config import FEEDBACK_FILE

# -------------------------
# Logging
# -------------------------
logger.add("logs/test_app_pipeline.log", rotation="5 MB", retention="7 days")
logger.info("Started test_app_pipeline.py script.")

def test_get_system_prompt_levels():
    topic = "AI"
    assert "simple language" in prompts.get_system_prompt(topic, "Middle School")
    assert "undergraduates" in prompts.get_system_prompt(topic, "College")
    assert "graduate students" in prompts.get_system_prompt(topic, "Advanced")

def test_get_user_prompt_includes_query_and_context():
    query = "What is AI?"
    context = "Artificial Intelligence is..."
    prompt = prompts.get_user_prompt(query, context)
    assert query in prompt
    assert context in prompt

def test_save_feedback_creates_file_and_writes(tmp_path):
    # Patch feedback_manager.FEEDBACK_FILE to a temp file
    orig_file = feedback_manager.FEEDBACK_FILE
    temp_file = tmp_path / "feedback.jsonl"
    feedback_manager.FEEDBACK_FILE = temp_file
    try:
        feedback_manager.save_feedback("Q", "A", "AI", "College", "up")
        assert temp_file.exists(), "No feedback file created"
        content = temp_file.read_text()
        assert "Q" in content and "A" in content
    finally:
        feedback_manager.FEEDBACK_FILE = orig_file

def mock_qdrant_query_points(*args, **kwargs):
    class MockResult:
        points = [
            MagicMock(payload={"context": "Mocked context"}, id=1, score=0.99)
        ]
    return MockResult()

def mock_embed_text(text):
    return [0.1, 0.2, 0.3]

def mock_openai_completion(*args, **kwargs):
    class MockResponse:
        choices = [MagicMock(message=MagicMock(content="This is a mocked GPT response."))]
    return MockResponse()

@patch("sciencesage.retrieval_system.qdrant")
@patch("sciencesage.retrieval_system.client")
def test_retrieve_answer_returns_answer_context_and_references(mock_openai_client, mock_qdrant_client):
    # Mock Qdrant
    mock_qdrant_client.query_points.side_effect = mock_qdrant_query_points
    # Mock OpenAI embedding and completion
    mock_openai_client.embeddings.create.return_value = MagicMock(data=[MagicMock(embedding=[0.1, 0.2, 0.3])])
    mock_openai_client.chat.completions.create.side_effect = mock_openai_completion

    answer, context, references = retrieval_system.retrieve_answer(
        "What is AI?", "AI", "College"
    )
    assert isinstance(answer, str)
    assert context is not None
    assert isinstance(references, list)