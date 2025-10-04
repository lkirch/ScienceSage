import pytest

from scripts import rag_llm_evaluation

# Mock dependencies
class DummyChunk:
    def __init__(self, chunk_id, text):
        self.chunk_id = chunk_id
        self.text = text
    def get(self, key):
        return getattr(self, key, None)

def dummy_retrieve_context(query, top_k=1, topic=None):
    return [DummyChunk("chunk123", "Sample context text.")]

def dummy_generate_answer(query, context_chunks, level, topic):
    return "Sample Answer"

def test_simple_exact_match():
    assert rag_llm_evaluation.simple_exact_match("Answer", "answer") == 1.0
    assert rag_llm_evaluation.simple_exact_match("Answer", "different") == 0.0
    assert rag_llm_evaluation.simple_exact_match("", "answer") == 0.0
    assert rag_llm_evaluation.simple_exact_match("answer", "") == 0.0

def test_load_and_save_jsonl(tmp_path):
    data = [{"a": 1}, {"b": 2}]
    file_path = tmp_path / "test.jsonl"
    rag_llm_evaluation.save_jsonl(data, str(file_path))
    loaded = rag_llm_evaluation.load_jsonl(str(file_path))
    assert loaded == data

def test_generate_llm_eval_for_entry(monkeypatch):
    # Patch retrieval and answer generation
    monkeypatch.setattr(rag_llm_evaluation, "retrieve_context", dummy_retrieve_context)
    monkeypatch.setattr(rag_llm_evaluation, "generate_answer", dummy_generate_answer)
    monkeypatch.setattr(rag_llm_evaluation, "TOP_K", 1)

    entry = {
        "question": "What is the answer?",
        "answer": "Sample Answer",
        "chunk_id": "chunk123",
        "topic": "Test Topic",
        "level": "College"
    }
    result = rag_llm_evaluation.generate_llm_eval_for_entry(entry)
    assert result["query"] == entry["question"]
    assert result["retrieved_answer"] == "Sample Answer"
    assert result["exact_match"] == 1.0
    assert result["context_ids"] == ["chunk123"]
    assert result["precision_at_k"] >= 0.0
    assert result["recall_at_k"] >= 0.0
    assert result["reciprocal_rank"] >= 0.0
    assert result["ndcg_at_k"] >= 0.0

def test_generate_llm_eval_for_entry_invalid(monkeypatch):
    monkeypatch.setattr(rag_llm_evaluation, "retrieve_context", dummy_retrieve_context)
    monkeypatch.setattr(rag_llm_evaluation, "generate_answer", dummy_generate_answer)
    with pytest.raises(ValueError):
        rag_llm_evaluation.generate_llm_eval_for_entry({"question": None, "answer": "x"})
