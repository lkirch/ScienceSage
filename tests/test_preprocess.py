import os
import json
from pathlib import Path
import pytest

from scripts import preprocess

def test_chunk_text_by_paragraphs_basic():
    text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
    paragraphs = preprocess.chunk_text_by_paragraphs(text)
    assert paragraphs == ["Paragraph one.", "Paragraph two.", "Paragraph three."]

def test_chunk_text_by_paragraphs_single_newline():
    text = "Para one.\nPara two.\nPara three."
    paragraphs = preprocess.chunk_text_by_paragraphs(text)
    assert paragraphs == ["Para one.", "Para two.", "Para three."]

def test_filter_categories_excludes_prefixes():
    categories = [
        "Category:Articles needing cleanup",
        "Category:Planets",
        "Category:CS1 errors",
        "Category:Space missions"
    ]
    filtered = preprocess.filter_categories(categories)
    assert "Category:Planets" in filtered
    assert "Category:Space missions" in filtered
    assert "Category:Articles needing cleanup" not in filtered
    assert "Category:CS1 errors" not in filtered

def test_infer_topic_planets():
    meta = {"categories": ["Category:Planets"]}
    topic = preprocess.infer_topic(meta)
    assert topic == "planets"

def test_make_standard_chunk_fields():
    text = "Sample paragraph."
    meta = {
        "title": "Mars",
        "fullurl": "https://en.wikipedia.org/wiki/Mars",
        "categories": ["Category:Planets"],
        "images": [],
        "summary": "Mars is a planet.",
    }
    chunk = preprocess.make_standard_chunk(text, meta, 0, 0, len(text))
    # Check required fields
    for field in preprocess.STANDARD_CHUNK_FIELDS:
        assert field in chunk

@pytest.fixture
def sample_raw_files(tmp_path):
    txt_path = tmp_path / "mars.txt"
    meta_path = tmp_path / "mars.meta.json"
    txt_path.write_text("Mars is the fourth planet.\n\nIt is red.")
    meta = {
        "title": "Mars",
        "fullurl": "https://en.wikipedia.org/wiki/Mars",
        "categories": ["Category:Planets"],
        "images": [],
        "summary": "Mars is a planet.",
    }
    meta_path.write_text(json.dumps(meta))
    return tmp_path

def test_main_creates_chunks_file(monkeypatch, tmp_path, sample_raw_files):
    monkeypatch.setattr(preprocess, "RAW_DATA_DIR", str(sample_raw_files))
    monkeypatch.setattr(preprocess, "CHUNKS_FILE", str(tmp_path / "chunks.jsonl"))
    preprocess.main()
    chunks_file = tmp_path / "chunks.jsonl"
    assert chunks_file.exists()
    lines = chunks_file.read_text().splitlines()
    assert len(lines) > 0
    chunk = json.loads(lines[0])
    assert "text" in chunk
    assert "topic" in chunk