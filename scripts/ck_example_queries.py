import os
import json

from sciencesage.retrieval_system import retrieve_context, generate_answer
from sciencesage.config import (
    LEVELS,
    EXAMPLE_QUERIES,
    TOP_K,
    EXAMPLE_QUERY_SUMMARY_FILE,
    logger,
)

# Ensure logs directory exists
os.makedirs(os.path.dirname(EXAMPLE_QUERY_SUMMARY_FILE), exist_ok=True)

def simple_pass_fail(answer: str) -> str:
    # Placeholder: mark as "PASS" if answer is non-empty, else "FAIL"
    return "PASS" if answer and answer.strip() else "FAIL"

def main():
    logger.info("Testing Qdrant retrieval for all example queries...")
    summary_records = []
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
                answer = generate_answer(query, chunks, level, topic)
                pass_fail = simple_pass_fail(answer)
                print(f"    Answer: {answer[:100]}... [{pass_fail}]")
            else:
                answer = ""
                pass_fail = "FAIL"
                print("    No chunks retrieved.\n")
            summary_records.append({
                "topic": topic,
                "level": level,
                "query": query,
                "answer": answer,
                "pass_fail": pass_fail
            })
        print("-" * 60)
    # Save summary as JSONL
    with open(EXAMPLE_QUERY_SUMMARY_FILE, "w") as f:
        for rec in summary_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Summary written to {EXAMPLE_QUERY_SUMMARY_FILE}")

if __name__ == "__main__":
    main()