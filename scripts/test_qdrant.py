
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
import numpy as np
import inspect
from loguru import logger

# Ensure project root is in sys.path for config import
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.config import QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION

# -------------------------
# Logging
# -------------------------
logger.add("logs/test_qdrant.log", rotation="5 MB", retention="7 days")
logger.info("Started test_qdrant.py script.")

# Load environment variables
load_dotenv()

def list_collections(client):
    logger.info("Available collections:")
    try:
        collections = client.get_collections().collections
        for c in collections:
            logger.info(f" - {c.name}")
    except Exception as e:
        logger.error(f"Failed to list collections: {e}")

def list_topics_and_counts(client, collection_name):
    logger.info(f"Listing all unique topics and their point counts in '{collection_name}':")
    topic_counts = {}
    offset = None
    try:
        while True:
            points, next_offset = client.scroll(
                collection_name=collection_name,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )
            for point in points:
                topic = point.payload.get("topic")
                if topic:
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
            if not next_offset:
                break
            offset = next_offset
        logger.info(f"Found {len(topic_counts)} unique topics:")
        for topic in sorted(topic_counts):
            logger.info(f" - {topic}: {topic_counts[topic]}")
    except Exception as e:
        logger.error(f"Failed to list topics and counts: {e}")
    return topic_counts

def show_collection_config(client, collection_name):
    logger.info(f"Schema/config for '{collection_name}':")
    try:
        info = client.get_collection(collection_name)
        logger.info(info.config)
        vector_size = info.config.params.vectors.size
        logger.info(f"Vector size: {vector_size}")
        return info, vector_size
    except Exception as e:
        logger.error(f"Failed to get collection config: {e}")
        raise

def show_total_points(info):
    try:
        logger.info(f"Total chunks (points) in collection: {info.points_count}")
    except Exception as e:
        logger.error(f"Failed to show total points: {e}")

def fetch_random_point(client, collection_name):
    logger.info(f"Fetching a random point from '{collection_name}':")
    try:
        result = client.scroll(collection_name=collection_name, limit=1)
        if result[0]:
            logger.info(result[0][0])
        else:
            logger.info("No points found.")
    except Exception as e:
        logger.error(f"Failed to fetch random point: {e}")

def test_similarity_search(client, collection_name, vector_size):
    logger.info(f"Testing similarity search in '{collection_name}':")
    try:
        test_vector = np.random.rand(vector_size).tolist()
        result = client.query_points(
            collection_name=collection_name,
            query=test_vector,
            limit=3,
            with_payload=False,
            with_vectors=False
        )
        logger.info(f"Top 3 hits (may be random):")
        for scored_point in result.points:
            logger.info(f"  ID: {scored_point.id}, Score: {scored_point.score}")
    except Exception as e:
        logger.error(f"Failed similarity search: {e}")

def main():
    logger.info(f"Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}")
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    try:
        list_collections(client)
        info, vector_size = show_collection_config(client, QDRANT_COLLECTION)
        show_total_points(info)
        fetch_random_point(client, QDRANT_COLLECTION)
        list_topics_and_counts(client, QDRANT_COLLECTION)
        test_similarity_search(client, QDRANT_COLLECTION, vector_size)
    except Exception as e:
        logger.error(f"Error: {e}")
        logger.error(f"Collection '{QDRANT_COLLECTION}' not found or Qdrant is not running.")

if __name__ == "__main__":
    main()