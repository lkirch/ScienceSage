#!/usr/bin/env python3

import pandas as pd
from loguru import logger

def summarize_feedback(file="feedback.csv"):
    logger.info(f"Starting feedback summarization for file: {file}")
    try:
        df = pd.read_csv(file)
        logger.debug(f"Read {len(df)} rows from {file}")
        summary = df.groupby(["topic", "level", "feedback"]).size().unstack(fill_value=0)
        logger.info("\nFeedback Summary:\n" + str(summary))
        print(summary)
    except Exception as e:
        logger.error(f"Failed to summarize feedback: {e}")

if __name__ == "__main__":
    summarize_feedback("data/feedback/feedback.csv")