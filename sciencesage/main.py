import streamlit as st
from app.retrieval_system import retrieve_answer
from app.feedback_manager import save_feedback
from config.config import LEVELS, TOPICS
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="ScienceSage", layout="wide")

# Sage green hex: #9DC183
st.markdown(
    '<h1 style="color:#9DC183; font-size:2.5em; margin-bottom:0.2em;">🔬 ScienceSage</h1>',
    unsafe_allow_html=True
)
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
        st.session_state.answer = answer
        st.session_state.context = context
        st.session_state.last_query = query
        st.session_state.last_topic = topic
        st.session_state.last_level = level
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
        save_feedback(
            st.session_state.get("last_query", ""),
            st.session_state.get("answer", ""),
            st.session_state.get("last_topic", ""),
            st.session_state.get("last_level", ""),
            "up"
        )
        logger.info("User gave positive feedback")
with col2:
    if st.button("👎", key="down"):
        save_feedback(
            st.session_state.get("last_query", ""),
            st.session_state.get("answer", ""),
            st.session_state.get("last_topic", ""),
            st.session_state.get("last_level", ""),
            "down"
        )
        logger.info("User gave negative feedback")
with col3:
    if st.button("🔄 Regenerate", key="regen"):
        answer, context = retrieve_answer(query, topic, level)
        st.session_state.answer = answer
        st.session_state.context = context
        st.write(answer)
        logger.info("User requested answer regeneration")
