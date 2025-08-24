#!/usr/bin/env python3

import pandas as pd

def summarize_feedback(file="feedback.csv"):
    df = pd.read_csv(file)
    summary = df.groupby(["topic", "level", "feedback"]).size().unstack(fill_value=0)
    print("\nFeedback Summary:\n")
    print(summary)

if __name__ == "__main__":
    summarize_feedback("data/feedback/feedback.csv")