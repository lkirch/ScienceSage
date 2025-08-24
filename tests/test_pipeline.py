#!/usr/bin/env python3

import os
import tempfile
import shutil
import pytest
from app import feedback_manager, retrieval_system, prompts

# --- Unit Tests ---

def test_get_system_prompt_levels():
    topic = "AI"
    assert "simple language" in prompts.get_system_prompt(topic, "Middle School")
    assert "undergraduates" in prompts.get_system_prompt(topic, "College")
    assert "graduate students" in prompts.get_system_prompt(topic, "Advanced")

def test_get_user_prompt_includes_context():
    query = "What is AI?"
    context = "Artificial Intelligence is..."
    prompt = prompts.get_user_prompt(query, context)
    assert query in prompt
    assert context in prompt

def test_save_feedback_creates_file_and_writes(tmp_path):
    # Patch feedback file location
    orig_dir = feedback_manager.FEEDBACK_DIR
    orig_file = feedback_manager.FEEDBACK_FILE
    feedback_manager.FEEDBACK_DIR = str(tmp_path)
    feedback_manager.FEEDBACK_FILE = os.path.join(str(tmp_path), "feedback.csv")

    feedback_manager.save_feedback("Q", "A", "AI", "College", "up")
    assert os.path.exists(feedback_manager.FEEDBACK_FILE)
    with open(feedback_manager.FEEDBACK_FILE) as f:
        lines = f.readlines()
    assert any("AI" in line for line in lines)

    # Restore
    feedback_manager.FEEDBACK_DIR = orig_dir
    feedback_manager.FEEDBACK_FILE = orig_file

# --- Integration Test (requires Qdrant and OpenAI API) ---

@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY") or not os.getenv("QDRANT_URL"),
    reason="Requires OpenAI API key and Qdrant running"
)
def test_retrieve_answer_returns_answer_and_context(monkeypatch):
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

