import os
from pathlib import Path
from loguru import logger
from sciencesage.config import QDRANT_URL

# -------------------------
# Logging
# -------------------------
logger.add("logs/test_pipeline.log", rotation="5 MB", retention="7 days")
logger.info("Started test_pipeline.py script.")

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Construct QDRANT_URL from QDRANT_HOST and QDRANT_PORT
os.environ["QDRANT_URL"] = os.getenv("QDRANT_URL")

from sciencesage import feedback_manager, retrieval_system, prompts

# --- Unit Tests ---

def test_get_system_prompt_levels():
    topic = "AI"
    logger.info("Testing get_system_prompt for all levels.")
    assert "simple language" in prompts.get_system_prompt(topic, "Middle School")
    assert "undergraduates" in prompts.get_system_prompt(topic, "College")
    assert "graduate students" in prompts.get_system_prompt(topic, "Advanced")
    logger.success("test_get_system_prompt_levels passed.")

def test_get_user_prompt_includes_context():
    query = "What is AI?"
    context = "Artificial Intelligence is..."
    logger.info("Testing get_user_prompt includes query and context.")
    prompt = prompts.get_user_prompt(query, context)
    assert query in prompt
    assert context in prompt
    logger.success("test_get_user_prompt_includes_context passed.")

def test_save_feedback_creates_file_and_writes(tmp_path):
    logger.info("Testing save_feedback creates file and writes content.")
    # Patch feedback file location
    orig_file = feedback_manager.FEEDBACK_FILE
    feedback_manager.FEEDBACK_FILE = os.path.join(str(tmp_path), "feedback.csv")

    feedback_manager.save_feedback("Q", "A", "AI", "College", "up")
    assert os.path.exists(feedback_manager.FEEDBACK_FILE)
    with open(feedback_manager.FEEDBACK_FILE) as f:
        lines = f.readlines()
    assert any("AI" in line for line in lines)

    # Restore
    feedback_manager.FEEDBACK_FILE = orig_file
    logger.success("test_save_feedback_creates_file_and_writes passed.")

import pytest

# --- Integration Test (requires Qdrant and OpenAI API) ---

@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY") or not os.getenv("QDRANT_URL"),
    reason="Requires OpenAI API key and Qdrant running"
)
def test_retrieve_answer_returns_answer_and_context(monkeypatch):
    logger.info("Testing retrieve_answer returns answer and context (integration test with monkeypatching).")
    # Monkeypatch embed_text to avoid real API call
    monkeypatch.setattr(retrieval_system, "embed_text", lambda text: [0.0]*1536)
    # Monkeypatch qdrant.query_points to return fake context
    class DummyPoint:
        def __init__(self, text): self.payload = {"text": text}
    class DummyResults:
        points = [DummyPoint("context1"), DummyPoint("context2")]
    monkeypatch.setattr(retrieval_system.qdrant, "query_points", lambda **kwargs: DummyResults())
    # Monkeypatch OpenAI completion
    class DummyChoice:
        class Message: content = "This is an answer."
        message = Message()
    class DummyCompletion:
        choices = [DummyChoice()]
    monkeypatch.setattr(retrieval_system.client.chat.completions, "create", lambda **kwargs: DummyCompletion())

    answer, contexts = retrieval_system.retrieve_answer("What is AI?", "AI", "College")
    assert "answer" in answer
    assert isinstance(contexts, list)
    assert len(contexts) > 0
    assert "context1" in contexts[0]
    assert "context2" in contexts[1]

