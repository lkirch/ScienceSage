import os
import json
from datetime import datetime, timezone
from loguru import logger
from sciencesage.config import FEEDBACK_FILE

def save_feedback(query, answer, topic, level, feedback_type):
    """
    Save feedback as a JSONL record to FEEDBACK_FILE.
    Each line is a JSON object with all fields.
    """
    logger.debug(f"save_feedback called with {query=}, {answer=}, {topic=}, {level=}, {feedback_type=}")
    logger.debug(f"FEEDBACK_FILE = {FEEDBACK_FILE}")
    feedback_dir = os.path.dirname(FEEDBACK_FILE)
    try:
        os.makedirs(feedback_dir, exist_ok=True)
        feedback_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query": query,
            "answer": answer,
            "topic": topic,
            "level": level,
            "feedback": feedback_type,
        }
        with open(FEEDBACK_FILE, mode="a", encoding="utf-8") as f:
            f.write(json.dumps(feedback_record, ensure_ascii=False) + "\n")
        logger.info("Feedback written successfully")
    except Exception as e:
        logger.error(f"ERROR writing feedback: {e}")