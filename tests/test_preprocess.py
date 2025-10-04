import pytest
import uuid
import datetime

from scripts.preprocess import (
    chunk_text_by_paragraphs,
    filter_categories,
    infer_topic,
    make_standard_chunk,
)

# --- chunk_text_by_paragraphs ---
def test_chunk_text_by_paragraphs_basic_split():
    text = "Para1.\n\nPara2 is longer.\n\nPara3."
    chunks = chunk_text_by_paragraphs(text, min_length=5, max_length=50)
    assert len(chunks) == 3
    assert chunks[0] == "Para1."
    assert chunks[1] == "Para2 is longer."
    assert chunks[2] == "Para3."

def test_chunk_text_by_paragraphs_merge_short():
    text = "Short1.\n\nShort2."
    chunks = chunk_text_by_paragraphs(text, min_length=15, max_length=50)
    # Should merge both
    assert len(chunks) == 1
    assert "Short1." in chunks[0] and "Short2." in chunks[0]

def test_chunk_text_by_paragraphs_split_long():
    text = "Sentence one. Sentence two. Sentence three."
    # Make max_length small to force split
    chunks = chunk_text_by_paragraphs(text, min_length=5, max_length=20)
    # Should split into multiple chunks by sentences
    assert all(len(c) <= 20 for c in chunks)
    assert any("Sentence one." in c for c in chunks)

def test_chunk_text_by_paragraphs_empty():
    assert chunk_text_by_paragraphs("") == []

def test_chunk_text_by_paragraphs_single_line():
    text = "Just one paragraph."
    chunks = chunk_text_by_paragraphs(text)
    assert chunks == ["Just one paragraph."]

# --- filter_categories ---
def test_filter_categories_excludes_prefixes():
    cats = [
        "Category:Articles with short description",
        "Category:Physics",
        "Category:Wikipedia pages",
        "Category:Commons",
        "Category:Science",
    ]
    filtered = filter_categories(cats)
    # Should exclude those with EXCLUDED_CATEGORY_PREFIXES
    assert "Category:Physics" in filtered
    assert "Category:Science" in filtered
    assert "Category:Articles with short description" not in filtered
    assert "Category:Wikipedia pages" not in filtered
    assert "Category:Commons" not in filtered

def test_filter_categories_no_excluded():
    cats = ["Category:Physics", "Category:Science"]
    filtered = filter_categories(cats)
    assert filtered == cats

def test_filter_categories_empty():
    assert filter_categories([]) == []

# --- infer_topic ---
def test_infer_topic_mars_title():
    meta = {"title": "Exploring Mars", "categories": []}
    assert infer_topic(meta) == "mars"

def test_infer_topic_mars_category():
    meta = {"title": "Other", "categories": ["Mars missions"]}
    assert infer_topic(meta) == "mars"

def test_infer_topic_moon():
    meta = {"title": "Moon Landing", "categories": []}
    assert infer_topic(meta) == "moon"

def test_infer_topic_space_exploration():
    meta = {"title": "Space Exploration", "categories": []}
    assert infer_topic(meta) == "space exploration"

def test_infer_topic_animals_in_space():
    meta = {"title": "Animals in Space", "categories": []}
    assert infer_topic(meta) == "animals in space"

def test_infer_topic_planets_category():
    meta = {"title": "Other", "categories": ["Gas planet"]}
    assert infer_topic(meta) == "planets"

def test_infer_topic_other():
    meta = {"title": "Random", "categories": ["Unrelated"]}
    assert infer_topic(meta) == "other"

# --- make_standard_chunk ---
def test_make_standard_chunk_fields():
    text = "Some chunk text."
    meta = {
        "title": "Mars Mission",
        "fullurl": "http://example.com",
        "categories": ["Mars", "Category:Commons"],
        "images": ["img1.jpg"],
        "summary": "Summary here.",
    }
    chunk = make_standard_chunk(text, meta, chunk_index=0, char_start=0, char_end=len(text))
    # Should contain only CHUNK_FIELDS keys
    from sciencesage.config import CHUNK_FIELDS
    assert set(chunk.keys()) <= set(CHUNK_FIELDS)
    assert chunk["text"] == text
    assert chunk["title"] == meta["title"]
    assert chunk["source_url"] == meta["fullurl"]
    assert chunk["chunk_index"] == 0
    assert chunk["char_start"] == 0
    assert chunk["char_end"] == len(text)
    assert isinstance(chunk["chunk_id"], str)
    assert chunk["topic"] == "mars"
    assert chunk["categories"] == ["Mars"]  # filtered
    assert isinstance(chunk["created_at"], str)

def test_make_standard_chunk_uuid_consistency():
    text = "Same text"
    meta = {"title": "SameTitle", "categories": []}
    chunk1 = make_standard_chunk(text, meta, 0, 0, 9)
    chunk2 = make_standard_chunk(text, meta, 1, 0, 9)
    # chunk_id should be the same for same title+text
    assert chunk1["chunk_id"] == chunk2["chunk_id"]

def test_make_standard_chunk_category_filtering():
    text = "Text"
    meta = {"title": "Title", "categories": ["Category:Commons", "Science"]}
    chunk = make_standard_chunk(text, meta, 0, 0, 4)
    assert "Category:Commons" not in chunk["categories"]
    assert "Science" in chunk["categories"]