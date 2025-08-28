#!/usr/bin/env python3

import os
import csv
from datetime import datetime, timezone
from loguru import logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEEDBACK_DIR = os.path.join(BASE_DIR, "data", "feedback")
FEEDBACK_FILE = os.path.join(FEEDBACK_DIR, "feedback.csv")

def save_feedback(query, answer, topic, level, feedback_type):
    """Save feedback to CSV file."""
    logger.debug(f"save_feedback called with {query=}, {answer=}, {topic=}, {level=}, {feedback_type=}")
    logger.debug(f"FEEDBACK_FILE = {FEEDBACK_FILE}")
    try:
        os.makedirs(FEEDBACK_DIR, exist_ok=True)
        file_exists = os.path.isfile(FEEDBACK_FILE)
        with open(FEEDBACK_FILE, mode="a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "query", "answer", "topic", "level", "feedback"])
            writer.writerow([datetime.now(timezone.utc), query, answer, topic, level, feedback_type])
        logger.info("Feedback written successfully")
    except Exception as e:
        logger.error(f"ERROR writing feedback: {e}")