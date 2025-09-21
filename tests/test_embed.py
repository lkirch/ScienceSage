from qdrant_client.models import PointStruct

def test_point_payload_contains_reference_urls():
    """Simulate a chunk and ensure reference_urls are preserved."""
    chunk = {
        "id": "chunk1",
        "uuid": "abc123",
        "topics": ["AI"],
        "source": "wikipedia",
        "chunk_index": 0,
        "text": "AI is cool.",
        "reference_urls": ["http://example.com"],
        "loadtime": "2025-09-06"
    }
    point = PointStruct(
        id="test",
        vector=[0.1, 0.2, 0.3],
        payload=chunk
    )
    assert "reference_urls" in point.payload
    assert point.payload["reference_urls"] == ["http://example.com"]

def test_point_payload_contains_standard_fields():
    """Simulate a chunk and ensure all standard fields are present and correct."""
    chunk = {
        "uuid": "abc123",
        "text": "The Apollo missions were a series of space missions by NASA.",
        "title": "Apollo program",
        "source_url": "https://en.wikipedia.org/wiki/Apollo_program",
        "categories": ["Space exploration", "Category:Space missions"],
        "images": ["https://example.com/apollo.jpg"],
        "summary": "NASA's Apollo program landed humans on the Moon.",
        "chunk_index": 0,
        "char_start": 0,
        "char_end": 100,
        "created_at": "2025-09-06T12:00:00Z",
        "topics": ["Space exploration", "Category:Space missions"]
    }
    point = PointStruct(
        id="test",
        vector=[0.1] * 1536,  # match EMBEDDING_DIM from config.py
        payload=chunk
    )
    # Check all standard fields
    for field in [
        "uuid", "text", "title", "source_url", "categories", "images", "summary",
        "chunk_index", "char_start", "char_end", "created_at", "topics"
    ]:
        assert field in point.payload
    assert "Space exploration" in point.payload["topics"]
    assert point.payload["title"] == "Apollo program"
    assert point.payload["source_url"].startswith("https://en.wikipedia.org/")
