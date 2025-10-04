import json
import uuid
from pathlib import Path
from typing import List, Dict
import argparse
from tqdm import tqdm
import pandas as pd
from loguru import logger

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
logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
model = SentenceTransformer(EMBEDDING_MODEL)
logger.info(f"Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}")
qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# -------------------------
# Helpers
# -------------------------
def load_chunks(path: Path) -> List[Dict]:
    logger.info(f"Loading chunks from {path} ...")
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def get_embedding(text: str) -> List[float]:
    return model.encode(text).tolist()

def ensure_collection(vector_size: int):
    collections = qdrant.get_collections().collections
    existing = [c.name for c in collections]
    if QDRANT_COLLECTION not in existing:
        logger.info(f"Creating collection '{QDRANT_COLLECTION}' ...")
        qdrant.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=vector_size, distance=chosen_distance)
        )
    else:
        logger.info(f"Collection '{QDRANT_COLLECTION}' already exists.")

def drop_collection():
    collections = qdrant.get_collections().collections
    existing = [c.name for c in collections]
    if QDRANT_COLLECTION in existing:
        logger.info(f"Dropping collection '{QDRANT_COLLECTION}' ...")
        qdrant.delete_collection(collection_name=QDRANT_COLLECTION)
    else:
        logger.info(f"Collection '{QDRANT_COLLECTION}' does not exist, skipping drop.")

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
        logger.error("No chunks found. Run preprocess.py first.")
        return

    ensure_collection(EMBEDDING_DIM)

    points = []
    embeddings_records = []
    for i, chunk in enumerate(tqdm(chunks, desc="Embedding and uploading chunks")):
        vector = get_embedding(chunk["text"])
        point_id = chunk.get("uuid") or str(uuid.uuid5(uuid.NAMESPACE_DNS, str(chunk)))
        payload = {k: chunk.get(k) for k in CHUNK_FIELDS if k != "embedding"}
        payload["embedding"] = vector
        payload["chunk_id"] = point_id
        points.append(
            PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            )
        )
        record = payload.copy()
        record["chunk_id"] = point_id
        embeddings_records.append(record)
        if len(points) >= QDRANT_BATCH_SIZE:
            # --- Sanity check before upload ---
            for p in points:
                if p.payload.get("chunk_id") is None:
                    logger.warning(f"Point with id {p.id} has chunk_id=None in payload!")
            logger.info(f"Uploading batch of {len(points)} points to Qdrant ...")
            qdrant.upsert(collection_name=QDRANT_COLLECTION, points=points)
            points = []

    if points:
        # --- Sanity check before final upload ---
        for p in points:
            if p.payload.get("chunk_id") is None:
                logger.warning(f"Point with id {p.id} has chunk_id=None in payload!")
        logger.info(f"Uploading final batch of {len(points)} points to Qdrant ...")
        qdrant.upsert(collection_name=QDRANT_COLLECTION, points=points)

    # Save embeddings to parquet
    df = pd.DataFrame(embeddings_records)
    df.to_parquet(EMBEDDING_FILE, index=False)
    logger.info(f"Saved embeddings to parquet: {EMBEDDING_FILE}")

    # --- Parquet sanity check: show first few records ---
    logger.info("Parquet file sample (first 5 rows):")
    df_check = pd.read_parquet(EMBEDDING_FILE)
    logger.info(f"\n{df_check.head()}")

if __name__ == "__main__":
    main()
