#!/usr/bin/env python3

import os
import json
from pathlib import Path
from typing import List, Dict
import uuid

from dotenv import load_dotenv 

from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

# -------------------------
# Load environment variables
# -------------------------
load_dotenv()  # Load variables from .env if present

# -------------------------
# Config
# -------------------------
CHUNKS_PATH = Path("data/chunks/chunks.jsonl")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = "scientific_concepts"
EMBED_MODEL = "text-embedding-3-small"   # or "text-embedding-3-large"

# -------------------------
# Clients
# -------------------------
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


# -------------------------
# Helpers
# -------------------------
def load_chunks(path: Path) -> List[Dict]:
    """Load chunks from jsonl file."""
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def get_embedding(text: str) -> List[float]:
    """Fetch embedding from OpenAI."""
    response = openai_client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )
    return response.data[0].embedding


def ensure_collection(vector_size: int):
    """Create collection in Qdrant if not exists."""
    collections = qdrant.get_collections().collections
    existing = [c.name for c in collections]

    if COLLECTION_NAME not in existing:
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )
        print(f"✅ Created Qdrant collection '{COLLECTION_NAME}'")
    else:
        print(f"ℹ️ Using existing Qdrant collection '{COLLECTION_NAME}'")


# -------------------------
# Main
# -------------------------
def main():
    print(f"Loading chunks from {CHUNKS_PATH}...")
    chunks = load_chunks(CHUNKS_PATH)

    if not chunks:
        print("❌ No chunks found. Run preprocess.py first.")
        return

    # Quick embedding to check vector size
    sample_vector = get_embedding("test")
    vector_size = len(sample_vector)
    ensure_collection(vector_size)

    # Upload chunks
    points = []
    for chunk in chunks:
        vector = get_embedding(chunk["text"])
        # Use the 'uuid' field from preprocess.py as the point ID (string)
        point_id = chunk.get("uuid", str(uuid.uuid5(uuid.NAMESPACE_DNS, str(chunk["id"]))))
        point = PointStruct(
            id=point_id,
            vector=vector,
            payload={
                "topic": chunk["topic"],
                "source": chunk["source"],
                "chunk_index": chunk["chunk_index"],
                "text": chunk["text"],
                "loadtime": chunk.get("loadtime")  # include loadtime if present
            }
        )
        points.append(point)

    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"✅ Uploaded {len(points)} chunks to Qdrant collection '{COLLECTION_NAME}'")


if __name__ == "__main__":
    main()
