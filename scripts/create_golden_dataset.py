import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from loguru import logger

from sciencesage.config import TOPICS, TOPIC_KEYWORDS, LEVELS

GOLDEN_DATA_FILE = Path("data/eval/golden_dataset.jsonl")
GOLDEN_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

logger.add("logs/create_golden_data.log", rotation="5 MB", retention="7 days", level="INFO")


def load_existing_examples():
    """Load existing golden examples into memory."""
    if GOLDEN_DATA_FILE.exists():
        with open(GOLDEN_DATA_FILE, "r") as f:
            return [json.loads(line) for line in f]
    return []


def save_example(example):
    """Append a single example to the golden dataset file."""
    with open(GOLDEN_DATA_FILE, "a") as f:
        f.write(json.dumps(example) + "\n")
    logger.info(f"Added new golden example: {example['id']}")


def interactive_add_examples():
    """Interactive CLI loop to add golden examples."""
    print("\n=== ScienceSage Golden Dataset Creator ===")
    print("Press Ctrl+C at any time to exit.\n")

    existing = load_existing_examples()
    print(f"Currently loaded {len(existing)} examples.")

    while True:
        try:
            # Select topic
            print("\nSelect a topic:")
            for i, topic in enumerate(TOPICS, start=1):
                print(f"  {i}. {topic}")
            print(f"  {len(TOPICS)+1}. Add a NEW topic")

            topic_choice = input(f"Enter choice [1-{len(TOPICS)+1}]: ").strip()
            if not topic_choice.isdigit() or int(topic_choice) not in range(1, len(TOPICS)+2):
                print("Invalid choice, try again.")
                continue

            topic_choice = int(topic_choice)
            if topic_choice == len(TOPICS)+1:
                topic = input("Enter new topic name: ").strip()
                logger.info(f"New topic created: {topic}")
            else:
                topic = TOPICS[topic_choice-1]

            # Select level
            print("\nSelect education level:")
            for i, level in enumerate(LEVELS, start=1):
                print(f"  {i}. {level}")
            level_choice = input(f"Enter choice [1-{len(LEVELS)}]: ").strip()
            if not level_choice.isdigit() or int(level_choice) not in range(1, len(LEVELS)+1):
                print("Invalid choice, try again.")
                continue
            level = LEVELS[int(level_choice)-1]

            # Enter Q&A
            question = input("\nEnter question: ").strip()
            expected_answer = input("Enter expected answer (short reference answer): ").strip()
            reference_urls = input("Enter reference URLs (comma separated, optional): ").strip()
            reference_urls = [u.strip() for u in reference_urls.split(",")] if reference_urls else []

            # Build example
            example = {
                "id": str(uuid.uuid4()),
                "topic": topic,
                "level": level,
                "question": question,
                "expected_answer": expected_answer,
                "reference_urls": reference_urls,
                "metadata": {
                    "created_at": datetime.utcnow().isoformat(),
                    "keywords": TOPIC_KEYWORDS.get(topic, []),
                }
            }

            # Save example
            save_example(example)
            print(f"✅ Added example for topic '{topic}' [{level}]")

            cont = input("\nAdd another? (y/n): ").strip().lower()
            if cont != "y":
                print("Exiting.")
                break

        except KeyboardInterrupt:
            print("\nExiting gracefully.")
            break


if __name__ == "__main__":
    interactive_add_examples()
