import streamlit as st
from retrieval_system import retrieve_answer
from feedback_manager import save_feedback
import sys
from pathlib import Path
# Ensure project root is in sys.path for config import
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.config import LEVELS, TOPICS
from loguru import logger

st.set_page_config(page_title="ScienceSage", layout="wide")

st.title("🔬 ScienceSage")
st.markdown('<span style="font-size:1.2em;color:gray;">"Smart Science, Made Simple."</span>', unsafe_allow_html=True)

# Sidebar
st.sidebar.header("Controls")
topic = st.sidebar.selectbox("Choose a topic", TOPICS)
level = st.sidebar.radio("Select explanation level", LEVELS)
example_queries = {
    "Neuroplasticity": ["What is neuroplasticity?", "How do neurons rewire?"],
    "AI": ["What is a neural network?", "Explain transformers."],
    "Renewable Energy & Climate Change": ["What is the greenhouse effect?", "How do solar panels work?"],
    "Animal Adaptation": ["How do penguins stay warm?", "What is mimicry in animals?"],
    "Ecosystem Interactions": ["What is a food chain?", "How does deforestation affect biodiversity?"]
}

if st.sidebar.button("Try Example"):
    st.session_state.query = example_queries[topic][0]

query = st.text_input("Enter your question:", key="query")

def infer_topic_from_query(query):
    for t in TOPICS:
        if t.lower().split()[0] in query.lower():
            return t
    return TOPICS[0]  # fallback

if st.button("Get Answer"):
    used_topic = topic or infer_topic_from_query(query)
    if not topic:
        st.warning("Please select a topic from the sidebar.")
    elif query.strip():
        logger.info(f"User submitted query: '{query[:50]}...', topic: '{used_topic}', level: '{level}'")
        with st.spinner("Retrieving answer..."):
            try:
                answer, context = retrieve_answer(query, used_topic, level)
                logger.info("Answer successfully retrieved")
            except Exception as e:
                logger.error(f"Error retrieving answer: {e}")
                st.error("An error occurred while retrieving the answer.")
                answer, context = None, None
        st.subheader("Answer")
        st.write(answer)

        with st.expander("Show retrieved context"):
            if context:
                if isinstance(context, (list, tuple)):
                    st.markdown("\n\n".join(str(c) for c in context))
                else:
                    st.markdown(str(context))
            else:
                st.info("No context retrieved.")

        # Feedback
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("👍", key="up"):
                save_feedback(query, answer, topic, level, "up")
                logger.info("User gave positive feedback")
        with col2:
            if st.button("👎", key="down"):
                save_feedback(query, answer, topic, level, "down")
                logger.info("User gave negative feedback")
        with col3:
            if st.button("🔄 Regenerate", key="regen"):
                answer, context = retrieve_answer(query, topic, level)
                logger.info("User requested answer regeneration")
                st.write(answer)
    else:
        st.warning("Please enter a question.")
