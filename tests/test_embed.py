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
