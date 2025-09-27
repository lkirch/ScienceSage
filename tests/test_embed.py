import pytest
from pathlib import Path

from scripts.embed import (
    load_chunks,
    get_embedding,
    ensure_collection,
    drop_collection,
)

class DummyQdrantClient:
    def __init__(self):
        self.collections = []
    def get_collections(self):
        class C:
            collections = [type("Col", (), {"name": "test_collection"})()]
        return C()
    def create_collection(self, collection_name, vectors_config):
        self.collections.append(collection_name)
    def delete_collection(self, collection_name):
        self.collections = [c for c in self.collections if c != collection_name]

def test_load_chunks(tmp_path):
    data = {"text": "abc", "uuid": "123"}
    file = tmp_path / "chunks.jsonl"
    with open(file, "w", encoding="utf-8") as f:
        f.write(f"{data}\n".replace("'", '"'))
    chunks = load_chunks(file)
    assert isinstance(chunks, list)
    assert chunks[0]["text"] == "abc"

def test_get_embedding_shape():
    text = "Hello world"
    emb = get_embedding(text)
    assert isinstance(emb, list)
    assert all(isinstance(x, float) for x in emb)
    # Embedding dim should match config
    from sciencesage.config import EMBEDDING_DIM
    assert len(emb) == EMBEDDING_DIM

def test_ensure_collection(monkeypatch):
    dummy = DummyQdrantClient()
    monkeypatch.setattr("scripts.embed.qdrant", dummy)
    monkeypatch.setattr("scripts.embed.QDRANT_COLLECTION", "new_collection")
    monkeypatch.setattr("scripts.embed.VectorParams", lambda size, distance: None)
    ensure_collection(10)
    assert "new_collection" in dummy.collections

def test_drop_collection(monkeypatch):
    dummy = DummyQdrantClient()
    dummy.collections = ["test_collection"]
    monkeypatch.setattr("scripts.embed.qdrant", dummy)
    monkeypatch.setattr("scripts.embed.QDRANT_COLLECTION", "test_collection")
    drop_collection()
    assert "test_collection" not in dummy.collections