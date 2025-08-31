import os
import sys
from pathlib import Path
import csv
from datetime import datetime, timezone
from loguru import logger

# Ensure project root is in sys.path for config import
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.config import FEEDBACK_FILE

def save_feedback(query, answer, topic, level, feedback_type):
    """Save feedback to CSV file."""
    logger.debug(f"save_feedback called with {query=}, {answer=}, {topic=}, {level=}, {feedback_type=}")
    logger.debug(f"FEEDBACK_FILE = {FEEDBACK_FILE}")
    feedback_dir = os.path.dirname(FEEDBACK_FILE)
    try:
        os.makedirs(feedback_dir, exist_ok=True)
        file_exists = os.path.isfile(FEEDBACK_FILE)
        with open(FEEDBACK_FILE, mode="a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "query", "answer", "topic", "level", "feedback"])
            writer.writerow([datetime.now(timezone.utc), query, answer, topic, level, feedback_type])
        logger.info("Feedback written successfully")
    except Exception as e:
        logger.error(f"ERROR writing feedback: {e}")