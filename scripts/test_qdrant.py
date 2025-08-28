#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
import numpy as np
import inspect
from loguru import logger

# Load environment variables
load_dotenv()

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = "scientific_concepts"

def list_collections(client):
    logger.info("Available collections:")
    collections = client.get_collections().collections
    for c in collections:
        logger.info(f" - {c.name}")

def list_topics_and_counts(client, collection_name):
    logger.info(f"Listing all unique topics and their point counts in '{collection_name}':")
    # Scroll through all points and collect topics
    topic_counts = {}
    offset = None
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
    return topic_counts

def show_collection_config(client, collection_name):
    logger.info(f"Schema/config for '{collection_name}':")
    info = client.get_collection(collection_name)
    logger.info(info.config)
    vector_size = info.config.params.vectors.size
    logger.info(f"Vector size: {vector_size}")
    return info, vector_size

def show_total_points(info):
    logger.info(f"Total chunks (points) in collection: {info.points_count}")

def fetch_random_point(client, collection_name):
    logger.info(f"Fetching a random point from '{collection_name}':")
    result = client.scroll(collection_name=collection_name, limit=1)
    if result[0]:
        logger.info(result[0][0])
    else:
        logger.info("No points found.")

def test_similarity_search(client, collection_name, vector_size):
    logger.info(f"Testing similarity search in '{collection_name}':")
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

def main():
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    try:
        list_collections(client)
        info, vector_size = show_collection_config(client, COLLECTION_NAME)
        show_total_points(info)
        fetch_random_point(client, COLLECTION_NAME)
        list_topics_and_counts(client, COLLECTION_NAME)
        test_similarity_search(client, COLLECTION_NAME, vector_size)
    except Exception as e:
        logger.error(f"Error: {e}")
        logger.error(f"Collection '{COLLECTION_NAME}' not found or Qdrant is not running.")

if __name__ == "__main__":
    main()