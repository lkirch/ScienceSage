import json
import uuid
from pathlib import Path
from typing import List, Dict
import argparse
from tqdm import tqdm
import pandas as pd

from sciencesage.config import (
    EMBEDDING_MODEL,
    EMBEDDING_DIM,
    CHUNKS_FILE,
    CHUNK_FIELDS,
    QDRANT_HOST,
    QDRANT_PORT,
    QDRANT_COLLECTION,
    QDRANT_BATCH_SIZE,
    EMBEDDING_FILE,
    DISTANCE_METRIC
)
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

# -------------------------
# Distance metric mapping
# -------------------------
distance_map = {
    "Cosine": Distance.COSINE,
    "Euclidean": Distance.EUCLID,
    "Dot": Distance.DOT
}
chosen_distance = distance_map.get(DISTANCE_METRIC, Distance.COSINE)

# -------------------------
# Model and Qdrant setup
# -------------------------
model = SentenceTransformer(EMBEDDING_MODEL)
qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# -------------------------
# Helpers
# -------------------------
def load_chunks(path: Path) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def get_embedding(text: str) -> List[float]:
    return model.encode(text).tolist()

def ensure_collection(vector_size: int):
    collections = qdrant.get_collections().collections
    existing = [c.name for c in collections]
    if QDRANT_COLLECTION not in existing:
        qdrant.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=vector_size, distance=chosen_distance)
        )

def drop_collection():
    collections = qdrant.get_collections().collections
    existing = [c.name for c in collections]
    if QDRANT_COLLECTION in existing:
        qdrant.delete_collection(collection_name=QDRANT_COLLECTION)

# -------------------------
# Main
# -------------------------
def main():
    parser = argparse.ArgumentParser(description="Embed and upload chunks to Qdrant.")
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to existing collection instead of dropping and recreating."
    )
    args = parser.parse_args()

    if not args.append:
        drop_collection()

    chunks = load_chunks(Path(CHUNKS_FILE))
    if not chunks:
        print("No chunks found. Run preprocess.py first.")
        return

    ensure_collection(EMBEDDING_DIM)

    points = []
    embeddings_records = []
    for chunk in tqdm(chunks, desc="Embedding and uploading chunks"):
        vector = get_embedding(chunk["text"])
        point_id = chunk.get("uuid") or str(uuid.uuid5(uuid.NAMESPACE_DNS, str(chunk)))
        payload = {k: chunk.get(k) for k in CHUNK_FIELDS if k != "embedding"}
        payload["embedding"] = vector
        points.append(
            PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            )
        )
        record = payload.copy()
        record["id"] = point_id
        embeddings_records.append(record)
        if len(points) >= QDRANT_BATCH_SIZE:
            qdrant.upsert(collection_name=QDRANT_COLLECTION, points=points)
            points = []

    if points:
        qdrant.upsert(collection_name=QDRANT_COLLECTION, points=points)

    # Save embeddings to parquet
    df = pd.DataFrame(embeddings_records)
    df.to_parquet(EMBEDDING_FILE, index=False)
    print(f"Saved embeddings to parquet: {EMBEDDING_FILE}")

if __name__ == "__main__":
    main()
