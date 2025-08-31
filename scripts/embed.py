
import os
import sys
from pathlib import Path
import json
from typing import List, Dict
import uuid
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from loguru import logger

# Ensure project root is in sys.path for config import
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.config import CHUNKS_FILE, QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION, EMBED_MODEL

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
            model=EMBED_MODEL,
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



# -------------------------
# Main
# -------------------------
def main():
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

    # Upload chunks
    points = []
    for chunk in chunks:
        try:
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
            logger.debug(f"Prepared point for chunk id: {point_id}")
        except Exception as e:
            logger.error(f"Failed to process chunk: {e}")

    try:
        qdrant.upsert(collection_name=QDRANT_COLLECTION, points=points)
        logger.info(f"Uploaded {len(points)} chunks to QDRANT collection '{QDRANT_COLLECTION}'")
    except Exception as e:
        logger.error(f"Failed to upload points to Qdrant: {e}")

if __name__ == "__main__":
    main()
