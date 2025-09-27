import os
from pathlib import Path
import json
from typing import List, Dict
import uuid
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from loguru import logger
import argparse
from tqdm import tqdm
import time
import pandas as pd

from sciencesage.config import (
    CHUNKS_FILE, 
    EMBEDDING_FILE, 
    QDRANT_HOST, 
    QDRANT_PORT, 
    QDRANT_COLLECTION, 
    EMBEDDING_MODEL,
    QDRANT_BATCH_SIZE, 
    STANDARD_CHUNK_FIELDS,
)

# -------------------------
# Logging
# -------------------------
logger.add("logs/embed.log", rotation="5 MB", retention="7 days")
logger.info("Started embed.py script.")

# -------------------------
# Load environment variables
# -------------------------
load_dotenv()  # Load variables from .env if present

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
    logger.info(f"Loading chunks from {path}...")
    try:
        with open(path, "r", encoding="utf-8") as f:
            chunks = [json.loads(line) for line in f]
        logger.info(f"Loaded {len(chunks)} chunks.")
        return chunks
    except Exception as e:
        logger.error(f"Failed to load chunks: {e}")
        return []

def get_embedding(text: str) -> List[float]:
    """Fetch embedding from OpenAI."""
    logger.debug(f"Getting embedding for text (first 50 chars): {text[:50]}...")
    try:
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        logger.debug("Embedding fetched successfully.")
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Failed to get embedding: {e}")
        raise

def ensure_collection(vector_size: int):
    """Create collection in Qdrant if not exists."""
    try:
        collections = qdrant.get_collections().collections
        existing = [c.name for c in collections]

        if QDRANT_COLLECTION not in existing:
            qdrant.create_collection(
                collection_name=QDRANT_COLLECTION,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
            logger.info(f"Created Qdrant collection '{QDRANT_COLLECTION}'")
        else:
            logger.info(f"Using existing Qdrant collection '{QDRANT_COLLECTION}'")
    except Exception as e:
        logger.error(f"Failed to ensure Qdrant collection: {e}")
        raise

def drop_collection():
    """Delete the Qdrant collection if it exists."""
    try:
        collections = qdrant.get_collections().collections
        existing = [c.name for c in collections]
        if QDRANT_COLLECTION in existing:
            qdrant.delete_collection(collection_name=QDRANT_COLLECTION)
            logger.info(f"Dropped existing Qdrant collection '{QDRANT_COLLECTION}'")
    except Exception as e:
        logger.error(f"Failed to drop Qdrant collection: {e}")
        raise

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

    # Quick embedding to check vector size
    try:
        sample_vector = get_embedding("test")
        vector_size = len(sample_vector)
        logger.debug(f"Sample embedding vector size: {vector_size}")
    except Exception as e:
        logger.error(f"Failed to get sample embedding: {e}")
        return

    try:
        ensure_collection(vector_size)
    except Exception as e:
        logger.error(f"Failed to ensure collection: {e}")
        return

    # Batch upload chunks with tqdm and elapsed time
    points = []
    failed_chunks = []
    embeddings_records = []  # <-- collect for parquet
    start_time = time.time()
    for idx, chunk in enumerate(tqdm(chunks, desc="Embedding and uploading chunks")):
        try:
            vector = get_embedding(chunk["text"])
            point_id = chunk.get("uuid") or str(uuid.uuid5(uuid.NAMESPACE_DNS, str(chunk)))
            payload = {k: chunk.get(k) for k in STANDARD_CHUNK_FIELDS if k != "embedding"}
            payload["embedding"] = vector
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            )
            # Save embedding record for parquet
            record = payload.copy()
            record["id"] = point_id
            embeddings_records.append(record)
            # Upload in batches
            if len(points) >= QDRANT_BATCH_SIZE:
                try:
                    qdrant.upsert(collection_name=QDRANT_COLLECTION, points=points)
                    logger.info(f"Uploaded {len(points)} chunks to QDRANT collection '{QDRANT_COLLECTION}'")
                    points = []
                except Exception as e:
                    logger.error(f"Failed to upload batch to Qdrant: {e}")
                    failed_chunks.extend([p.payload.get("id", "unknown") for p in points])
                    points = []
        except Exception as e:
            chunk_id = chunk.get("id", "unknown")
            logger.error(f"Failed to process chunk id {chunk_id}: {e}")
            failed_chunks.append(chunk_id)

    # Upload any remaining points
    if points:
        try:
            qdrant.upsert(collection_name=QDRANT_COLLECTION, points=points)
            logger.info(f"Uploaded {len(points)} chunks to QDRANT collection '{QDRANT_COLLECTION}'")
        except Exception as e:
            logger.error(f"Failed to upload final batch to Qdrant: {e}")
            failed_chunks.extend([p.payload.get("id", "unknown") for p in points])

    # Save embeddings to parquet
    try:
        df = pd.DataFrame(embeddings_records)
        df.to_parquet(EMBEDDING_FILE, index=False)
        logger.info(f"Saved embeddings to parquet: {EMBEDDING_FILE}")
    except Exception as e:
        logger.error(f"Failed to save embeddings to parquet: {e}")

    elapsed = time.time() - start_time
    logger.info(f"Elapsed time: {elapsed:.2f} seconds")

    if failed_chunks:
        logger.warning(f"Failed to embed/upload {len(failed_chunks)} chunks. IDs: {failed_chunks}")
    else:
        logger.info("All chunks embedded and uploaded successfully.")

if __name__ == "__main__":
    main()
