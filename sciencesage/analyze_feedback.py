import pandas as pd
from loguru import logger
from sciencesage.config import FEEDBACK_FILE

def summarize_feedback(file=FEEDBACK_FILE):
    logger.info(f"Starting feedback summarization for file: {file}")
    try:
        df = pd.read_json(file, lines=True)
        logger.debug(f"Read {len(df)} rows from {file}")
        summary = df.groupby(["topic", "level", "feedback"]).size().unstack(fill_value=0)
        logger.info("\nFeedback Summary:\n" + str(summary))
        print(summary)
    except Exception as e:
        logger.error(f"Failed to summarize feedback: {e}")

if __name__ == "__main__":
    summarize_feedback()