import streamlit as st
import pandas as pd
import json
from collections import Counter
from sciencesage.config import TOPICS, LEVELS

FEEDBACK_FILE = "data/feedback/feedback.jsonl"

st.set_page_config(page_title="ScienceSage Feedback Dashboard", layout="wide")
st.title("🛰️ ScienceSage User Feedback Dashboard")

# Load feedback data
def load_feedback(feedback_file):
    records = []
    try:
        with open(feedback_file, "r") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
    except FileNotFoundError:
        st.warning("No feedback data found.")
    return pd.DataFrame(records)

df = load_feedback(FEEDBACK_FILE)

if df.empty:
    st.info("No feedback available yet.")
    st.stop()

# Preprocessing
df['feedback'] = df['feedback'].map({'thumbs_up': '👍', 'thumbs_down': '👎'}).fillna(df['feedback'])
df['topic'] = df['topic'].astype('category')
df['level'] = df['level'].astype('category')

# 1. Thumbs up/down count
st.subheader("1. Overall Feedback Count")
feedback_counts = df['feedback'].value_counts()
st.bar_chart(feedback_counts)

# 2. Thumbs up rate by topic
st.subheader("2. Thumbs Up Rate by Topic")
topic_group = df.groupby(['topic', 'feedback']).size().unstack(fill_value=0)
topic_group['Thumbs Up Rate'] = topic_group.get('👍', 0) / topic_group.sum(axis=1)
st.bar_chart(topic_group['Thumbs Up Rate'])

# 3. Thumbs up rate by education level
st.subheader("3. Thumbs Up Rate by Education Level")
level_group = df.groupby(['level', 'feedback']).size().unstack(fill_value=0)
level_group['Thumbs Up Rate'] = level_group.get('👍', 0) / level_group.sum(axis=1)
st.bar_chart(level_group['Thumbs Up Rate'])

# 4. Most frequent queries
st.subheader("4. Most Frequent Queries")
top_queries = df['query'].value_counts().head(10)
st.table(top_queries)

# 5. Feedback distribution by topic (stacked bar)
st.subheader("5. Feedback Distribution by Topic")
feedback_by_topic = df.groupby(['topic', 'feedback']).size().unstack(fill_value=0)
st.bar_chart(feedback_by_topic)

# Raw data
with st.expander("Show Raw Feedback Data"):
    st.dataframe(df)