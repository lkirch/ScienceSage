#!/usr/bin/env python3

import csv
from datetime import datetime
import os

FEEDBACK_DIR = "data/feedback"
FEEDBACK_FILE = os.path.join(FEEDBACK_DIR, "feedback.csv")

def save_feedback(query, answer, topic, level, feedback_type):
    """Save feedback to CSV file."""
    os.makedirs(FEEDBACK_DIR, exist_ok=True)
    file_exists = os.path.isfile(FEEDBACK_FILE)

    with open(FEEDBACK_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "query", "answer", "topic", "level", "feedback"])
        writer.writerow([datetime.utcnow(), query, answer, topic, level, feedback_type])