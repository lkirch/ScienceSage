#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

# Load environment variables
load_dotenv()

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = "scientific_concepts"

def main():
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    try:
        info = client.get_collection(COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' exists.")
        print(f"Total chunks (points) in collection: {info.points_count}")
    except Exception as e:
        print(f"Error: {e}")
        print(f"Collection '{COLLECTION_NAME}' not found or Qdrant is not running.")

if __name__ == "__main__":
    main()