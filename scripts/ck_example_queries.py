from loguru import logger
from sciencesage.retrieval_system import retrieve_context
from sciencesage.config import LEVELS, EXAMPLE_QUERIES, TOP_K
import os

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

logger.add("logs/ck_example_queries.log", level="DEBUG")

def main():
    logger.info("Testing Qdrant retrieval for all example queries...")
    for topic, queries in EXAMPLE_QUERIES.items():
        logger.info(f"Topic: {topic}")
        print(f"Topic: {topic}")
        for level_idx, query in enumerate(queries):
            level = LEVELS[level_idx]
            logger.debug(f"Level: {level} | Query: {query}")
            print(f"  Level: {level}")
            print(f"    Query: {query}")
            chunks = retrieve_context(query, top_k=TOP_K, topic=topic)
            logger.debug(f"Retrieved chunks: {len(chunks)}")
            print(f"    Retrieved chunks: {len(chunks)}")
            if chunks:
                for i, chunk in enumerate(chunks):
                    logger.debug(f"[{i+1}] Score: {chunk['score']:.4f} | Text: {chunk['text'][:100]}...")
                    print(f"    [{i+1}] Score: {chunk['score']:.4f} | Text: {chunk['text'][:100]}...")
                print()
            else:
                logger.warning("No chunks retrieved.")
                print("    No chunks retrieved.\n")
        print("-" * 60)

if __name__ == "__main__":
    main()